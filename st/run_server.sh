#!/bin/bash
# This script should run every 5 mins

log=/opt2/jhe010/st/log/django.log
home=/opt2/jhe010/st/

# Check if there is exception happening, which brings down the web server
line=`grep "Exception" $log`
length=${#line}
if [[ $length -gt 0 ]] 
then
    # If so, stop the server
    ps aux | grep 'python manage.py runserver 0.0.0.0:6001'| while read line 
    do
        if [[ $line == *grep* ]]
        then
            continue
        fi
        pid=`echo $line | cut -f 2 -d " "`
        kill $pid &> $log".cron"
    done
fi


# Restart
nline=`ps aux | grep 'python manage.py runserver 0.0.0.0:6001' | wc -l`
if [[ $nline -eq 1 ]] 
then
    # restart the server
    python $home/manage.py runserver 0.0.0.0:6001 &> $log &
fi




