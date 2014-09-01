"""
Indexing documents from the KB news collection.
"""

from elasticsearch import Elasticsearch, RequestError, ConnectionError
import requests 
from urllib import quote, unquote
import params as p
import argparse
import sys, re
import datetime
import xml.etree.ElementTree as et 
from string_util import string_to_unicode, html_unescape
import itertools
import 

# Namespace of the downloaded records
namespace_ddd = {
    "srw": "http://www.loc.gov/zing/srw/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "ddd": "http://www.kb.nl/ddd",
}


es = Elasticsearch()

def create_index():
    """
        Create index and put mapping of document structure. 
        If the index for the given name exists, skip it. 
    """
    # Check if the index already exists
    if es.indices.exists(index=p.INDEX):
        print 'Index %s exists'%p.INDEX
    else:
        print 'Creat index %s'%p.INDEX
        es.indices.create(index=p.INDEX, body=p.SIM_SETTING)

    if es.indices.exists_type(index=p.INDEX, doc_type=p.DOC_TYPE):
        print 'Doc type exists: ', p.DOC_TYPE
    else:
        print 'Create mapping for doc_type %s'%p.DOC_TYPE
        es.indices.put_mapping(index=p.INDEX, doc_type=p.DOC_TYPE, body=p.MAPPING)


def add_document(document):
    """
        Add document to index
        Parameters:
        * document: a json object
    """
    es.index(index=p.INDEX, doc_type=p.DOC_TYPE, body=document, id=document['docid'])


# Requests encode the urls in a strange way
# we encode it in our way here
def encode_params(params):
    """
        Format the SRU retrieval parameters as url
        Parameters:
        * params: the SRU parameters stored in a dictionary 
    """
    return '&'.join(['%s=%s'%(key, params[key]) for key in params])

# Validate the input date
def validate_date(string):
    """
        Check if a date string is valid
        Parameters:
        * string: the input date string
    """
    try:
        date = datetime.datetime.strptime(string, '%d-%m-%Y')
    except:
        print 'String "%s" does not match the date format dd-mm-yyyy'%string 
        sys.exit()

def process_records(records):
    """
    From each record construct the document to be indexed
    A document should be in the following format:
    d = {
            'docid': 'identifier',
            'date': 'publishcing date',
            'loc': 'publishing location',
            'title': 'article title',
            'text': 'ocr content',
            'entity_person': None,
            'entity_orgnization': None,
            'entity_location': None,
        }

    Parameters:
    * records: the element srw:records from the retrieved result set
    """
    skip = []
    for record in records: 
        rd = record.find('srw:recordData', namespaces=namespace_ddd)
        # If no record data, skip this record
        if rd == None:
            continue

        # Location
        location_text = ''
        location = rd.find('ddd:spatial', namespaces=namespace_ddd)
        if not location == None:
            location_text = location.text 
        if not location_text in p.NEWS_LOC:
            skip.append(location_text)
            continue

        # Get title
        title = rd.find('dc:title', namespaces=namespace_ddd)
        title_text = ''
        if not title == None:
            title_text = title.text
        # Date
        date = rd.find('dc:date', namespaces=namespace_ddd)
        date_text = ''
        if not date == None:
            date_object = datetime.datetime.strptime(date.text, '%Y/%m/%d %H:%M:%S')
            date_text = '%s-%s-%s'%(date_object.year, date_object.month, date_object.day)

        # Newspaper title
        paper_title = ''
        papertitle = rd.find('ddd:papertitle', namespaces=namespace_ddd)
        if not papertitle == None:
            paper_title = papertitle.text

        # Get the OCR url
        identifier = rd.find('dc:identifier', namespaces=namespace_ddd)
        # Download OCR
        
        if identifier == None:
            print 'No OCR found:', rd.text 
            continue
        # Download ocr
        r = requests.get(identifier.text)

        # clean the text
        text = re.sub(r'<.+?>', '', r.content)
        text = html_unescape(string_to_unicode(text))
        #print text

        document = {
            'docid': identifier.text.replace(':ocr', '').split('urn=')[1],
            'text': text,
            'date': date_text, 
            'loc': location_text,
            'title': title_text,
            'paper_title': paper_title,
            'entity_person': None,
            'entity_orgnization': None,
            'entity_location': None,
        }
        #print document['docid']
        #print r.content

        # Add document to index
        add_document(document)
    #skip.sort()
    #for k, g in itertools.groupby(skip):
    #    print 'Skipped %s news from %s'%(len(list(g)), k)
    print 'Skipped news from other locations: %s'%len(skip) 

def index_documents(startdate, enddate):
    """
        Indexing documents retrieved from the KB news collection
        Parameters
        * startdate: download articles after and include this date
        * enddate: download articles before and include this date
    """
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
        'recordSchema': 'ddd',
        'operation': 'searchRetrieve',
        'x-collection': 'DDD_artikel',
        'maximumRecords': 1000,
        'startRecord': startRecord,
        'query': qry,
        }
    # Get the metadata of the result set
    # print encode_params(params)
    r = requests.get(url, params=encode_params(params))
    root = et.fromstring(r.content)
    count = 0
    count_record = root.find('srw:numberOfRecords', namespaces=namespace_ddd)
    if count_record == None:
        print 'No results were found.'
        sys.exit()
    else:
        count = int(count_record.text)
    print 'Total records:', count

    # Process downloaded records
    records = root.findall('srw:records', namespaces=namespace_ddd)
    all_records = records[0].findall('srw:record', namespaces=namespace_ddd)
    print 'processing', startRecord, '-', len(all_records)+startRecord-1, '/%s'%count 
    process_records(all_records)
   
    # Continue downloading if there are more results
    startRecord += 1000
    while startRecord <= count:
        params['startRecord'] = startRecord
        r = requests.get(url, params=encode_params(params))
        root = et.fromstring(r.content)
        records = root.findall('srw:records', namespaces=namespace_ddd)
        if len(records) == 0:
            print 'Error: No records retrieved'
            break

        all_records = records[0].findall('srw:record', namespaces=namespace_ddd)
        print 'processing', startRecord, '-', len(all_records)+startRecord-1, '/%s'%count
 
        process_records(all_records)
        startRecord += 1000


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('startdate', 
        help="The starting date of the documents to be indexed: dd-mm-yyyy")
    parser.add_argument('enddate',
        help="The end date of the documents to be indexed: dd-mm-yyyy")    
    args = parser.parse_args()

    validate_date(args.startdate)
    validate_date(args.enddate)

    create_index()    
    index_documents(args.startdate, args.enddate)
  


