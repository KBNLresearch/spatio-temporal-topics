# This script should run every 5 mins
line=`grep "Exception" django.log`
length=${#line}
if (( $length > 0 )) 
then
    ps aux | grep 'python manage.py runserver 0.0.0.0:6001'| while read line 
    do
        pid=`echo $line | cut -f 2 -d " "`
        kill $pid
    done
fi

line=`ps aux | grep 'python manage.py runserver 0.0.0.0:6001'`
length=${#line}
if (( $length == 1 ))
then
    # restart the server
    python manage.py runserver 0.0.0.0:6001 &> django.log &
fi




