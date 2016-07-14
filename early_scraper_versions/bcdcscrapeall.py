# coding: utf-8
# this is code from Acton Gorton



# import python libraries
from bs4 import BeautifulSoup
import urllib2
from urlparse import urlparse, parse_qs
import re
from mechanize import Browser
import lxml
import csv




# use mechanize to create a fake form submission
browser = Browser()
browser.open('http://app.bernco.gov/custodylist/CustodyListInter.aspx?submitted=true')
browser.select_form(nr=0)
browser['DescList'] = ['ALL']
response = browser.submit()
content = response.read()




# assign the results from mechanize to BeautifulSoup for parsing
inmate_soup = BeautifulSoup(content, 'lxml')
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
            
        # add to inmate_list
        inmate_list.append(inmate_personal)




# write the inmate personal details to a csv file
with open('inmate_details.csv', 'w') as csvfile:
    
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
        'inmate_desc'
    ]
    
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
                'inmate_desc': i[10]
            })




# ###################################################################################################################
# Because its possible for an inmate to have multiple arrest charges and a history or warrants and bails, 
# we'll create individual files for each of those situations and then use the unique inmate id to join those
# files later on. These files can be imported into a database as "one to many" relationships (one inmate, many things)
# ###################################################################################################################




# arrest csv writer
arrest_record = open('arrest_details.csv', 'a')

# define the column names
arrest_fieldnames = [
    'inmate_id',
    'case_number',
    'confirm',
    'arrest_date',
    'arrest_time',
    'arrest_location',
    'warrant_description',
    'warrant_comment'
]

# instantiate csv writing object
arrest_writer = csv.DictWriter(arrest_record, fieldnames=arrest_fieldnames)

# write the columns names
arrest_writer.writeheader()

# write the record
def write_arrest(inmate_id, data):
    arrest_writer.writerow({
        'inmate_id': inmate_id,
        'case_number': data[0],
        'confirm': data[1],
        'arrest_date': data[2],
        'arrest_time': data[3],
        'arrest_location': data[4],
        'warrant_description': data[5],
        'warrant_comment': data[6]
        })




# warrant csv writer
warrant_record = open('warrant_details.csv', 'a')

# define the column names
warrant_fieldnames = [
    'inmate_id',
    'case_number',
    'confirm',
    'arrest_date',
    'arrest_time',
    'arrest_location',
    'warrant_description',
    'warrant_comment'
]

# instantiate csv writing object
warrant_writer = csv.DictWriter(warrant_record, fieldnames=warrant_fieldnames)

# write the columns names
warrant_writer.writeheader()

# write the record
def write_bail(inmate_id, data):
    warrant_writer.writerow({
        'inmate_id': inmate_id,
        'case_number': data[0],
        'confirm': data[1],
        'arrest_date': data[2],
        'arrest_time': data[3],
        'arrest_location': data[4],
        'warrant_description': data[5],
        'warrant_comment': data[6]
        })




# bail csv writer
bail_record = open('bail_details.csv', 'a')

# define the column names
bail_fieldnames = [
    'inmate_id',
    'case_number',
    'bond_amount',
    'bond_desc'
]

# instantiate csv writing object
bail_writer = csv.DictWriter(bail_record, fieldnames=bail_fieldnames)

# write the columns names
bail_writer.writeheader()

# write the record
def write_bail(inmate_id, data):
    bail_writer.writerow({
        'inmate_id': inmate_id,
        'case_number': data[0],
        'bond_amount': data[1],
        'bond_desc': data[2]
        })




# arrest charges
def arrest_charges(inmate_id, data):
        
    # create a definition function to parse the buried details
    def parse_arrests(d):
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
        print '......', case_number, arrest_date, description
        arrest = [
            case_number,
            release_type,
            arrest_date,
            arrest_time,
            arrest_location,
            statute,
            description
        ]
        write_warrant(inmate_id, arrest)
    
    # but first we have to dig into these obnoxiously buried tables, one step at a time
    first_level = data.find('table')
    
    # go through each warrant record
    arrest_record = first_level.find('tr')
    while True:
        try:
            parse_arrests(arrest_record)
        except:
            pass
        
        if arrest_record.next_sibling:
            arrest_record = arrest_record.next_sibling
        else:
            break




# warrant history
def warrant_history(inmate_id, data):
        
    # create a definition function to parse the buried details
    def parse_warrants(d):
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
        print '......', case_number, confirm, arrest_date
        warrant = [
            case_number,
            confirm,
            arrest_date,
            arrest_time,
            arrest_location,
            warrant_desc,
            warrant_comm
        ]
        write_warrant(inmate_id, warrant)
    
    # but first we have to dig into these obnoxiously buried tables, one step at a time
    first_level = data.find('table')
    
    # go through each warrant record
    warrant_record = first_level.find('tr')
    while True:
        try:
            parse_warrants(warrant_record)
        except:
            pass
        
        if warrant_record.next_sibling:
            warrant_record = warrant_record.next_sibling
        else:
            break
    




# bail history
def bail_history(inmate_id, data):
    
    # create a definition function to parse the buried details
    def parse_bail(d):
        find_tables = d.find_all('table')
        num_tables = int(len(find_tables)) -1
        deepest_table = find_tables[num_tables]
        records = deepest_table.find_all('tr')
        
        # assign variable names
        case_number = records[0].find('span').get_text()
        bond_amount = records[1].find('span').get_text()
        bond_desc = records[2].find('span').get_text()
        
        # write each record to csv
        print '......', case_number, bond_amount, bond_desc
        bail = [case_number, bond_amount, bond_desc]
        write_bail(inmate_id, bail)
    
    # but first we have to dig into these obnoxiously buried tables, one step at a time
    first_level = data.find('table')
    
    # go through each record
    bail_record = first_level.find('tr')
    while True:
        try:
            parse_bail(bail_record)
        except:
            pass
        
        if bail_record.next_sibling:
            bail_record = bail_record.next_sibling
        else:
            break




# flow control parsers
def parse_inmate(inmate_id, data):
    
    # arrest charges
    if data.find(id='GridView2_Panel'):
        print '... gathering arrest records'
        arrest_charges(inmate_id, data.find(id='GridView2_Panel'))

    # warrant history
    if data.find(id='GridView3_Panel'):
        print '... gathering warrant records'
        warrant_history(inmate_id, data.find(id='GridView3_Panel'))
        
    # bail history
    if data.find(id='GridView4_Panel'):
        print '... gathering bail records'
        bail_history(inmate_id, data.find(id='GridView4_Panel'))




# setup python to fetch individual inmate details
url = 'http://app.bernco.gov/custodylist/'

# loop through inmate_list and fetch details:
for i in inmate_list:
    
    # assign variables for inmate id and link to inmate page
    inmate_id = i[2]
    inmate_link = i[1]
    
    # create the complete url link to the inmate's details
    inmate_url = url + inmate_link
    
    # print a status update to let us know what's going on
    print 'checking ', inmate_url
    
    # setup beautifulsoup to parse the page
    page = urllib2.urlopen(inmate_url)
    soup = BeautifulSoup(page, 'lxml')
    
    # send to parse_inmate definition
    parse_inmate(inmate_id, soup)
    
    # add a few spaces between the output to make it easier to read
    print '\n\n'
