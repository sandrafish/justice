import urllib2
import re
import os
import lxml
import csv
from datetime import datetime
from bs4 import BeautifulSoup
from urlparse import urlparse, parse_qs
from mechanize import Browser

class ReleasedInmateRecordScraper(object):

    def __init__(self):
        browser = Browser()
        browser.open('http://app.bernco.gov/custodylist/ReleaseListInter.aspx')
        browser.select_form(nr=0)
        response = browser.submit()

        # Set universal variable that can be read by other functions
        self.content = response.read()


    def inmate_exists(self, inmate):
        """ Checks to see whether csv already exists, and whether inmate is already in that existing csv """
        if os.path.isfile('data/released_inmates.csv'):
            if inmate in open("data/released_inmates.csv").read():
                return True
            else:
                return False
        else:
            return False


    def scrape_released_inmates(self):
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
                
                # inmate age
                inmate_age = inmate_details[3].get_text()
                
                # inmate gender
                inmate_gender = inmate_details[4].get_text()
                
                # inmate race
                inmate_race = inmate_details[5].get_text()
                
                # inmate release date
                inmate_release = inmate_details[6].get_text()
                
                # assign to temporary array
                inmate_personal = [
                        inmate_name, 
                        inmate_link, 
                        inmate_id, 
                        inmate_booking,
                        inmate_age,
                        inmate_gender,
                        inmate_race,
                        inmate_release,
                    ]
                
                # clean up each object in array
                for x in inmate_personal:
                    x = unicode(x).strip()

                # check exist existing table to see if that inmate has already been scraped
                if self.inmate_exists(inmate_personal[2]):
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
            'inmate_age',
            'inmate_gender',
            'inmate_race',
            'inmate_release',
            'date_scraped'
        ]

        # Checks to see if file already exists
        if os.path.isfile('data/released_inmates.csv'):

            # If it does, open up the file for appending
            with open('data/released_inmates.csv', 'a') as csvfile:

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                # Loop through entries in inmate list and append them to bottom of inmate_details.csv
                for i in inmate_list:
                    writer.writerow({
                        'inmate_name': i[0],
                        'inmate_link': i[1],
                        'inmate_id': i[2],
                        'inmate_booking': i[3],
                        'inmate_age': i[4],
                        'inmate_gender': i[5],
                        'inmate_race': i[6],
                        'inmate_release': i[7],
                        'date_scraped': datetime.today().date()
                    })
        

        else:
            # if file does not already exist, write the inmate personal details to a new csv file
            with open('data/released_inmates.csv', 'w') as csvfile:
                
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
                        'inmate_age': i[4],
                        'inmate_gender': i[5],
                        'inmate_race': i[6],
                        'inmate_release': i[7],
                        'date_scraped': datetime.today().date()
                    })
            
# Run the scrapers
if __name__ == "__main__":
    scraper = ReleasedInmateRecordScraper()
    inmates = scraper.scrape_released_inmates()

    # If there are any new inmates, write the and their records to files
    if len(inmates) > 0:
        print 'Writing ' + str(len(inmates)) + ' new inmates and their records to csv files.'
        scraper.write_inmates(inmates)
    else:
        print 'No new inmates.'

