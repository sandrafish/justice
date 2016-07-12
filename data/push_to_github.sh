#!/bin/bash  

# This script will run both the inmate and released inmates scraper, then push the results to github

python scraper.py
python release_scraper.py

git add . 
d=$(date +%y-%m-%d)
git commit -m "Adding data for $d"
git push