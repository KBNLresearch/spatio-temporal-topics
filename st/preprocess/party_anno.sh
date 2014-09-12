#!/bin/bash

# This script runs and checks indexing process while I am away.
# The KB retrieval service seems to have some problems
# if I have too many requests continuously. 
startyear=$1
endyear=$2

for (( year=$startyear; year<=$endyear; year++))
do
    echo $year 
    log=tmp.ner.log$year

    python runAnnotation.py 01-01-$year 31-12-$year ner >> $log
done

