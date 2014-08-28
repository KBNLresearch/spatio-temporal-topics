"""
Annotate documents from the KB news collection.

"""

from elasticsearch import Elasticsearch, RequestError, ConnectionError
from urllib import quote, unquote
import params as p
import argparse
import datetime
from Annotator import Annotator

es = Elasticsearch()
stat_field = 'text'

def process_docs(startdate, enddate, method):
    """
    Retrive documents within the date range
    @ Params
    startedate: starting date, inclusive
    enddate: ending date, inclusive
    method: annotate the documents with a specific method

    Methods include:
        - ner: using KB ner service + estimated importance of NERs
    """
    an = Annotator(method, field=stat_field)
    # Get the documents in this period
    qry = {
        'range': {
            'date': {
                'gte': startdate,
                'lte': enddate,
            }
        }
    }

    start = 0
    size = 1000
    records = []
    res = es.search(index=p.INDEX, 
        doc_type=p.DOC_TYPE, 
        body={'filter': qry}, 
        size=size, 
        from_=start,
        )
    records += [d['_id'] for d in res['hits']['hits']]
    total = res['hits']['total']

    start += size
    while start < total:
        res = es.search(index=p.INDEX, 
            doc_type=p.DOC_TYPE, 
            body={'filter': qry}, 
            size=size,
            from_=start,
            )
        #records = [d['_id'] for d in res['hits']['hits']]

        # Annoate the retrieved documents
        print "Annotating: %s - %s/%s"%(start, start+size, total)
        for d in res['hits']['hits']: 
            an.annotate(d['_id'])
        start += size     
    return records

# Validate the input date
def validate_date(string):
    """
        Check if a date string is valid
        Parameters:
        * string: the input date string
    """
    try:
        date = datetime.datetime.strptime(string, '%d-%m-%Y')
        day, month, year = string.split('-')
        return '%s-%s-%s'%(year, month, day)

    except:
        print 'String "%s" does not match the date format dd-mm-yyyy'%string 
        sys.exit()
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('startdate', 
        help="The starting date of the documents to be indexed: dd-mm-yyyy")
    parser.add_argument('enddate',
        help="The end date of the documents to be indexed: dd-mm-yyyy")
    parser.add_argument('method', 
        help="Method used to annotate the article, options: ner")
    args = parser.parse_args()

    startdate = validate_date(args.startdate)
    enddate = validate_date(args.enddate)

    process_docs(startdate, enddate, args.method)
  


