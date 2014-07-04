"""
Download the xml metadata news papers
and their ocred documents
"""
import sys
import re
import argparse
import requests 
from urllib import quote, unquote
import simplejson as js
import datetime
import os

reg_identifier = re.compile('<dc:identifier>.+?</dc:identifier>')
reg_record = re.compile('<srw:record>.+?</srw:record>')
reg_numrecords = re.compile('<srw:numberOfRecords>.+?</srw:numberOfRecords>')

def process_ocr(records, outputdir):
    # Download ocr
    for record in records: 
        match = reg_identifier.findall(record)
        if len(match) > 0:
            idx = match[0].split('>')[1].split('<')[0]
            r = requests.get(idx)
            # Save the downloaded
            f = open('%s/ocr/%s'%(outputdir, idx.split('/')[-1]), 'w')
            f.write(r.content)
            f.close()
        else:
            print 'No OCR found:', record

def download_metadata(startdate, enddate, outputdir):
    print 'Starting date:', startdate, 'Ending date:', enddate
    # Note: it seems that the API allows maximum 1000 records to be retrieved
    # The request url
    url = 'http://jsru.kb.nl/sru/sru?'
    startRecord = 1
    qry = quote('* and date within "%s %s" and type = artikel'%(
        startdate, enddate), safe='*=')
    #print qry
    # Download 1 result to get the total number of records
    params = {
        'operation': 'searchRetrieve',
        'x-collection': 'DDD_artikel',
        'maximumRecords': 1,
        'startRecord': startRecord,
        'query': qry,
        }
    r = requests.get(url, params=encode_params(params))    
    match = reg_numrecords.findall(r.content)
    count = 0
    if len(match)> 0:
        count = int(match[0].split('>')[1].split('<')[0])
    print 'Total records:', count

    # Now start download them in batch
    params['maximumRecords'] = 1000
    part = 1
    while startRecord <= count:
        params['startRecord'] = startRecord
        r = requests.get(url, params=encode_params(params))
        records = reg_record.findall(r.content)
        print 'processing', startRecord, '-', len(records)+startRecord-1, '/%s'%count

        # Save the metadata
        outputfile = '%s_%s.part%s.json'%(startdate, enddate, part)
        f = open('%s/meta/%s'%(outputdir, outputfile), 'w')
        js.dump(records, f)
        f.close()

        # Download the ocrs
        process_ocr(records, outputdir)
    
        # move on    
        startRecord += len(records)
        part += 1
        #if part == 3:
        #    break

# Requests encode the urls in a strange way
# we encode it in our way here
def encode_params(params):
    return '&'.join(['%s=%s'%(key, params[key]) for key in params])

def validate_date(string):
    try:
        date = datetime.datetime.strptime(string, '%d-%m-%Y')
    except:
        print 'String "%s" does not match the date format dd-mm-yyyy'%string 
        sys.exit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('startdate', 
        help="The starting date of the documents to be downloaded: dd-mm-yyyy")
    parser.add_argument('enddate',
        help="The end date of the documents to be downloaded: dd-mm-yyyy")    
    parser.add_argument('outputdir',
        help="The directory for storing the downloaded metadata and ocr data"
        )
    args = parser.parse_args()

    validate_date(args.startdate)
    validate_date(args.enddate)

    # make outputdir
    if os.path.exists(args.outputdir):
        if not os.path.exists('%s/meta/'%(args.outputdir)):
            os.mkdir('%s/meta'%args.outputdir)
        if not os.path.exists('%s/ocr/'%(args.outputdir)):
            os.mkdir('%s/ocr'%args.outputdir)
    else:
        print 'Output directory does not exist:%s'%args.outputdir
        sys.exit()

    download_metadata(args.startdate, args.enddate, args.outputdir)
    

