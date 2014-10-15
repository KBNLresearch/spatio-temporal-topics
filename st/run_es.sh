#!/bin/bash

# Run elasticsearch
if [ $# -lt 1 ]
then
    echo './run_es.sh options'
    echo 'options:'  
    echo 'start     to start elasticsearch'
    echo 'stop      to stop elasticsearch'
    exit
fi

HOME_ES=es/elasticsearch-1.2.2/
log=log/


if [[ "$1" == 'start' ]]
then
    $HOME_ES/bin/elasticsearch -Des.node.data=false -Des.node.master=true -Des.node.name=master &> log/es.master &
    $HOME_ES/bin/elasticsearch -Des.node.data=true -Des.node.master=false -Des.node.name=data &> log/es.data &
    $HOME_ES/bin/elasticsearch -Des.node.data=false -Des.node.master=false -Des.node.name=node3 &> log/es.node3 &
#$HOME_ES/bin/elasticsearch  &> log/es.node1 &
fi

if [[ "$1" == 'stop' ]]
then
    ps aux | grep 'elasticsearch'| while read line 
    do
        if [[ $line == *grep* ]]
        then
            continue
        fi 
        pid=`echo $line | cut -f 2 -d " "`
        kill $pid  
    done

fi
