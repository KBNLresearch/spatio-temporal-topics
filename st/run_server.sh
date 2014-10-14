# This script should run every 5 mins
log=log/django.log

line=`grep "Exception" $log`
length=${#line}
if (( $length > 0 )) 
then
    ps aux | grep 'python manage.py runserver 0.0.0.0:6001'| while read line 
    do
        pid=`echo $line | cut -f 2 -d " "`
        kill $pid
    done
fi

nline=`ps aux | grep 'python manage.py runserver 0.0.0.0:6001' | wc -l`
if (( $nline == 1 ))
then
    echo 'restart'
    # restart the server
    python manage.py runserver 0.0.0.0:6001 &> $log &
fi




