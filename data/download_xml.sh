#!/bin/bash


# To download the metadata of news articles
outputfile=1918-1940.xml
startdate=01-01-1918
enddate=31-12-1940


wget -O $outputfile "http://jsru.kb.nl/sru/sru?x-collection=DDD_artikel&query=*%20and%20date%20within%20%22$startdate%20$enddate%22%20and%20type%20=%20artikel"
