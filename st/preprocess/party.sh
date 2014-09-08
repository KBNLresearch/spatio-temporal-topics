#!/bin/bash

# This script runs and checks indexing process while I am away.
# The KB retrieval service seems to have some problems
# if I have too many requests continuously. 

to_index="to_index"
err_log="err_log"

cat $to_index | while read line
do
    echo $line
    python runIndexKBNews.py 01-01-$line 31-12-$line > tmp
    error=`grep 'Error' tmp`
    if [ "$error" != '' ]
    then
         echo $line >> $err_log
    fi     
    fail=`grep 'timeout' tmp`
    if [ "$fail" != '' ]
    then
        echo $line >> $err_log
    fi
done

cp $err_log $to_index
echo -n > $err_log
