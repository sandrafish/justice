# derived from bcdcscrapeall.py
# coding: utf-8



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


