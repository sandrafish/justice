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
        #get the idno that links all this shit
        ids = urlparse.parse_qs(url)
        idbo = ids.get('bo')
        
        soup = BeautifulSoup(open(url))
        #must use ab otherwise you only get one
        f = open('warrants.csv', 'ab')      
        writer = csv.writer(f)
       
        table3 = soup.find('table', attrs={'id':"DataList3"})
        try:
            for fmltable3 in table3.findAll('table'): # Inside our DataList2 table is an table holding the table contents for each charge.
                for warranttable in fmltable3.findAll('table'):   # Now we're looking at the actual charge table
                    list_of_fields_w = [idbo[0]]  # Pull out booking number thingy from list, just as a string.
                    #print list_of_fields
                    for field in warranttable.findAll('td'):
                        text = field.text.split("  ")[-1]       # Let's look for everything after a couple spaces. This seems to work.
                        list_of_fields_w.append(text)
                    
                    #this is a key indent otherwise it gets only one or multiples
                    writer.writerow(list_of_fields_w)     
            
        except:
            continue   
       
       
        
              
         # You still need to close out your csvwriter
        f.close()
        