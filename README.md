# BernCo Detention Data

Procedure:

  Actually have been manually copying and pasting the full list from [this site.] (http://app.bernco.gov/custodylist/CustodyListInter.aspx)
  
  Open in excel, add a URL column and use this macro to get the URLs from the ID column:
  
    Sub ExtractHL_AdjacentCell()
  
    Dim HL As Hyperlink
  
    For Each HL In ActiveSheet.Hyperlinks
  
        HL.Range.Offset(0, 1).Value = HL.Address
  
    Next

End Sub

  Copy and past the URLs into a urls.txt file in a folder with the date.

  From command line, wget -i urls.txt to download pages into that day's folder.

  Run basics.py, charges.py, warrants.py, bond.py to get .csv files for that day.
  
##Notes:

There's another file here, bcdcscrapeall.py, which should scrape the whole site. But i've not been able to get it to work on my local machine and it appears to be blocked. Also, i'd prefer to have the archived webpages for reference points.

Other issues:

  Need to automate the first section (instead of copying and pasting, etc.) and set it up to run on it's own. i'll work on the first part, but have no idea how to do the second.
  
  Need to add the date the info was retrieved as a field in the four scripts.
  
  There's also likely a way to run the four scripts from a single script if i went back and looked at the refactoring stuff from NICAR a few years ago.
  

  
