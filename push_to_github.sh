#!/bin/bash  

git add . 
d=$(date +%y-%m-%d)
git commit -m "Adding data for $d"
git push