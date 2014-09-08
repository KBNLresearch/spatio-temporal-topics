#!/bin/bash

start=1936
end=1940

for (( i=$start; i<=$end; i++ ))
do
    for (( j=1; j<=12; j++))
    do
        echo $j-$i
    done
done
