# code based on my original, modified by Mike Stucka (thus fml) and me
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urlparse
import os
from bs4 import BeautifulSoup
import urllib2
import csv

for i in os.listdir(os.getcwd()):
    if i.startswith('ChargesInter'):
        url = i
        ids = urlparse.parse_qs(url)
        idbo = ids.get('bo')
        #print idbo
        soup = BeautifulSoup(open(url))
        #above works
        f = open('charges.csv', 'ab')      
        writer = csv.writer(f)
       
        table2 = soup.find('table', attrs={'id':"DataList2"})
        try:
            for fmltable in table2.findAll('table'): # Inside our DataList2 table is an table holding the table contents for each charge.
                for chargetable in fmltable.findAll('table'):   # Now we're looking at the actual charge table
                    list_of_fields = [idbo[0]]  # Pull out booking number thingy from list, just as a string.
                    #print list_of_fields
                    for field in chargetable.findAll('td'):
                        text = field.text.split("  ")[-1]       # Let's look for everything after a couple spaces. This seems to work.
                        list_of_fields.append(text)
                        #print list_of_fields
        
                    writer.writerow(list_of_fields)     # Write it to CSV.
            
        except:
            continue   
       
       
        
              
         # You still need to close out your csvwriter
        f.close()
        