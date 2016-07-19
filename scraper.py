import urllib2
import re
import os
import lxml
import csv
from datetime import datetime
from bs4 import BeautifulSoup
from urlparse import urlparse, parse_qs
from mechanize import Browser

class InmateRecordScraper(object):

    def __init__(self):
        # Opens imitation browser and submits form
        browser = Browser()
        browser.open('http://app.bernco.gov/custodylist/CustodyListInter.aspx?submitted=true')
        browser.select_form(nr=0)
        browser['DescList'] = ['ALL']
        response = browser.submit()

        # Set universal variable that can be read by other functions
        self.content = response.read()


    def booking_number_already_scraped(self, booking_number):
        """ Checks to see whether csv already exists, and whether inmate is already in that existing csv """

        if os.path.isfile('data/inmate_details.csv'):
            if booking_number in open("data/inmate_details.csv").read():
                return True
            else:
                return False
        else:
            return False


    def scrape_inmates(self):
        """ Scrapes the inmate details from the web, appends them to list """

        # assign the results from mechanize to BeautifulSoup for parsing
        inmate_soup = BeautifulSoup(self.content, 'lxml')
        custody_list = inmate_soup.find('table', {'rules': 'all'})

        # create an array to hold each row of information about inmates
        inmate_list = []

        # parse through the table and add inmate information to the inmate_list
        for i in custody_list.find_all('tr'):

            # only retrieve rows with a hyperlink
            if i.find('a', href=True):

                # get all of the table data fields within the row
                inmate_details = i.find_all('td')

                # inmate name
                inmate_name = inmate_details[0].get_text()

                # inmate link
                inmate_link = str(i.find('a', href=True).get('href'))

                # inmate unique id
                inmate_id = inmate_details[1].get_text()

                # inmate booking id
                inmate_booking = inmate_details[2].get_text()

                # inmate birth year
                inmate_yob = inmate_details[3].get_text()

                # inmate age
                inmate_age = inmate_details[4].get_text()

                # inmate gender
                inmate_gender = inmate_details[5].get_text()

                # inmate race
                inmate_race = inmate_details[6].get_text()

                # inmate arrival date
                inmate_arrival = inmate_details[7].get_text()

                # inmate cell number
                inmate_cell = inmate_details[8].get_text()

                # inmate description field
                inmate_desc = inmate_details[9].get_text()

                # assign to temporary array
                inmate_personal = [
                        inmate_name,
                        inmate_link,
                        inmate_id,
                        inmate_booking,
                        inmate_yob,
                        inmate_age,
                        inmate_gender,
                        inmate_race,
                        inmate_arrival,
                        inmate_cell,
                        inmate_desc
                    ]

                # clean up each object in array
                for x in inmate_personal:
                    x = unicode(x).strip()

                # check exist existing table to see if that booking number has already been scraped
                # This used to check for ID number, but was changed to account for the possibility of multiple arrests in the study time
                if self.booking_number_already_scraped(inmate_personal[3]):
                    pass
                else:
                    # if not already in table add to inmate_list
                    inmate_list.append(inmate_personal)

        return inmate_list


    def write_inmates(self, inmate_list):
        """ Writes the inmates to a csv file """

        # define the column names
        fieldnames = [
            'inmate_name',
            'inmate_link',
            'inmate_id',
            'inmate_booking',
            'inmate_yob',
            'inmate_age',
            'inmate_gender',
            'inmate_race',
            'inmate_arrival',
            'inmate_cell',
            'inmate_desc',
            'date_scraped'
        ]

        # Checks to see if file already exists
        if os.path.isfile('data/inmate_details.csv'):

            # If it does, open up the file for appending
            with open('data/inmate_details.csv', 'a') as csvfile:

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Loop through entries in inmate list and append them to bottom of inmate_details.csv
                for i in inmate_list:
                    writer.writerow({
                        'inmate_name': i[0],
                        'inmate_link': i[1],
                        'inmate_id': i[2],
                        'inmate_booking': i[3],
                        'inmate_yob': i[4],
                        'inmate_age': i[5],
                        'inmate_gender': i[6],
                        'inmate_race': i[7],
                        'inmate_arrival': i[8],
                        'inmate_cell': i[9],
                        'inmate_desc': i[10],
                        'date_scraped': datetime.today().date()
                    })


        else:
            # if file does not already exist, write the inmate personal details to a new csv file
            with open('data/inmate_details.csv', 'w') as csvfile:

                # instantiate csv writing object
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # write the columns names
                writer.writeheader()

                # loop through inmate_list array and write the rows to the csv file:
                for i in inmate_list:
                    writer.writerow({
                        'inmate_name': i[0],
                        'inmate_link': i[1],
                        'inmate_id': i[2],
                        'inmate_booking': i[3],
                        'inmate_yob': i[4],
                        'inmate_age': i[5],
                        'inmate_gender': i[6],
                        'inmate_race': i[7],
                        'inmate_arrival': i[8],
                        'inmate_cell': i[9],
                        'inmate_desc': i[10],
                        'date_scraped': datetime.today().date()
                    })

    def case_number_already_in_table(self, file_name, case_number):
        if case_number in open(file_name).read():
            return True
        else:
            return False

    def write_arrest(self, inmate_id, data):
        """ writes the arrest records to a csv called arrest_details.csv """

        # define the column names
        arrest_fieldnames = ['inmate_id','case_number','confirm','arrest_date','arrest_time','arrest_location','warrant_description','warrant_comment','date_scraped']

        # If arrest_details already exists, open the file for appending

        with open('data/arrest_details.csv', 'a') as arrest_record:

            # Check to see if the arrest has already been recorded
            # This is specifically to make sure we don't duplicate arrest data on someone who was booked twice during the study period
            if self.case_number_already_in_table('data/arrest_details.csv', data[0]):
                print str(inmate_id) + ' Arrest already in table'
            else:
                # instantiate csv writing object
                arrest_writer = csv.DictWriter(arrest_record, fieldnames=arrest_fieldnames)

                # write the record (same as below)
                arrest_writer.writerow({
                    'inmate_id': inmate_id,
                    'case_number': data[0],
                    'confirm': data[1],
                    'arrest_date': data[2],
                    'arrest_time': data[3],
                    'arrest_location': data[4],
                    'warrant_description': data[5],
                    'warrant_comment': data[6],
                    'date_scraped': datetime.today().date()
                })


    def write_warrant(self, inmate_id, data):
        """ writes the warrant records to a csv called warrant_details.csv """

        # define the column names
        warrant_fieldnames = ['inmate_id','case_number','confirm','arrest_date','arrest_time','arrest_location','warrant_description','warrant_comment','date_scraped']

        with open('data/warrant_details.csv', 'a') as warrant_record:

            # Check to see if warrant is already in the table
            # This is specifically to make sure we don't duplicate warrant data on someone who was booked twice during the study period
            if self.case_number_already_in_table('data/warrant_details.csv', data[0]):
                print str(inmate_id) + ' Warrant already in table'
            else:
                # instantiate csv writing object
                warrant_writer = csv.DictWriter(warrant_record, fieldnames=warrant_fieldnames)

                # write the record (same as below)
                warrant_writer.writerow({
                    'inmate_id': inmate_id,
                    'case_number': data[0],
                    'confirm': data[1],
                    'arrest_date': data[2],
                    'arrest_time': data[3],
                    'arrest_location': data[4],
                    'warrant_description': data[5],
                    'warrant_comment': data[6],
                    'date_scraped': datetime.today().date()
                })



    def write_bail(self, inmate_id, data):
        """ writes the bail records to a csv called bail_details.csv """

        # define the column names
        bail_fieldnames = ['inmate_id','case_number','bond_amount','bond_desc','date_scraped']

        with open('data/bail_details.csv', 'a') as bail_record:

            # Check to see if this bail record has already been recorded
            # This is specifically to make sure we don't duplicate bail data on someone who was booked twice during the study period
            if self.case_number_already_in_table('data/bail_details.csv', data[0]):
                print str(inmate_id) +' Bail already in table'
            else:
                # instantiate csv writing object
                bail_writer = csv.DictWriter(bail_record, fieldnames=bail_fieldnames)

                # write the record (same as below)
                bail_writer.writerow({
                    'inmate_id': inmate_id,
                    'case_number': data[0],
                    'bond_amount': data[1],
                    'bond_desc': data[2],
                    'date_scraped': datetime.today().date()
                })


    # create a definition function to parse the buried details
    def parse_arrests(self, inmate_id, d):
        find_tables = d.find_all('table')
        num_tables = int(len(find_tables)) -1
        deepest_table = find_tables[num_tables]
        records = deepest_table.find_all('tr')

        # assign variable names
        case_number = records[0].find('span').get_text()
        release_type = records[1].find('span').get_text()
        arrest_date = records[2].find('span').get_text()
        arrest_time = records[3].find('span').get_text()
        arrest_location = records[4].find('span').get_text()
        statute = records[5].find('span').get_text()
        description = records[6].find('span').get_text()

        # write each record to csv
        arrest = [
            case_number,
            release_type,
            arrest_date,
            arrest_time,
            arrest_location,
            statute,
            description
        ]

        return (inmate_id, arrest)

        # Chained method -- must rewrite
        self.write_arrest(inmate_id, arrest)


    def find_arrest_charges(self, inmate_id, data):
        """ parses arrest charges section of individual inmate pages """

        # but first we have to dig into these obnoxiously buried tables, one step at a time
        first_level = data.find('table')

        # go through each warrant record
        arrest_record = first_level.find('tr')

        while True:
            try:
                return (inmate_id, arrest_record)
            except:
                pass

            if arrest_record.next_sibling:
                arrest_record = arrest_record.next_sibling
            else:
                break


    # create a definition function to parse the buried details
    def parse_warrants(self, inmate_id, d):
        find_tables = d.find_all('table')
        num_tables = int(len(find_tables)) -1
        deepest_table = find_tables[num_tables]
        records = deepest_table.find_all('tr')

        # assign variable names
        case_number = records[0].find('span').get_text()
        confirm = records[1].find('span').get_text()
        arrest_date = records[2].find('span').get_text()
        arrest_time = records[3].find('span').get_text()
        arrest_location = records[4].find('span').get_text()
        warrant_desc = records[5].find('span').get_text()
        warrant_comm = records[6].find('span').get_text()

        # write each record to csv
        warrant = [
            case_number,
            confirm,
            arrest_date,
            arrest_time,
            arrest_location,
            warrant_desc,
            warrant_comm
        ]

        return (inmate_id, warrant)


    def find_warrant_history(self, inmate_id, data):
        """ parses warrant history section of individual inmate pages """

        # but first we have to dig into these obnoxiously buried tables, one step at a time
        first_level = data.find('table')

        # go through each warrant record
        warrant_record = first_level.find('tr')

        while True:
            try:
                return (inmate_id, warrant_record)
            except:
                pass

            if warrant_record.next_sibling:
                warrant_record = warrant_record.next_sibling
            else:
                break


    def parse_bail(self, inmate_id, d):
        find_tables = d.find_all('table')
        num_tables = int(len(find_tables)) -1
        deepest_table = find_tables[num_tables]
        records = deepest_table.find_all('tr')

        # assign variable names
        case_number = records[0].find('span').get_text()
        bond_amount = records[1].find('span').get_text()
        bond_desc = records[2].find('span').get_text()

        # write each record to csv
        bail = [case_number, bond_amount, bond_desc]

        return (inmate_id, bail)


    def find_bail_history(self, inmate_id, data):
        """ parses bail history section of individual inmate pages """

        # but first we have to dig into these obnoxiously buried tables, one step at a time
        first_level = data.find('table')

        # go through each record
        bail_record = first_level.find('tr')

        print bail_record.get_text()
        print '______________'

        try:
            return (inmate_id, bail_record)
        except:
            pass

        try:
            next_records = bail_record.find_next_siblings('tr')
            print next_records
        except:
            print str(inmate_id) + ' has only one bail record'

        # if bail_record.next_sibling:
        #     print str(inmate_id) + 'Has next sibling!'
        #     bail_record = bail_record.next_sibling



    def get_individual_soup(self, inmate):
        """ fetches individual inmate details from each inmate url """

        base_url = 'http://app.bernco.gov/custodylist/'

        # assign variables for inmate id and link to inmate page
        inmate_id = inmate[2]
        inmate_link = inmate[1]

        # create the complete url link to the inmate's details
        inmate_url = base_url + inmate_link

        # setup beautifulsoup to parse the page
        page = urllib2.urlopen(inmate_url)
        soup = BeautifulSoup(page, 'lxml')

        # create a new file for the raw html out of today's date and the inmate's id
        file_name = str(datetime.today().date()) + '__' + str(inmate_id) + '.html'

        # write the raw page html to a new file
        with open('raw_pages/' + file_name, 'w') as raw_page:
            raw_page.write(str(soup))

        return (inmate_id, soup)


# Run the scrapers
if __name__ == "__main__":
    scraper = InmateRecordScraper()
    inmates = scraper.scrape_inmates()

    # If there are any new inmates, write the inmate and their records to files
    if len(inmates) > 0:
        print 'Writing ' + str(len(inmates)) + ' new booking records to csv files.'

        scraper.write_inmates(inmates)

        for inmate in inmates:
            inmate_id, soup = scraper.get_individual_soup(inmate)

            try:
                inmate_id, data = scraper.find_arrest_charges(inmate_id, soup.find(id='GridView2_Panel'))
                inmate_id, parsed_data = scraper.parse_arrests(inmate_id, data)
                scraper.write_arrest(inmate_id, parsed_data)
            except:
                pass

            try:
                inmate_id, data = scraper.find_warrant_history(inmate_id, soup.find(id='GridView3_Panel'))
                inmate_id, parsed_data = scraper.parse_warrants(inmate_id, data)
                scraper.write_warrant(inmate_id, parsed_data)
            except:
                pass

            try:
                inmate_id, data = scraper.find_bail_history(inmate_id, soup.find(id='GridView4_Panel'))
                inmate_id, parsed_data = scraper.parse_bail(inmate_id, data)
                scraper.write_bail(inmate_id, parsed_data)
            except:
                pass
    else:
        print 'No new bookings.'
