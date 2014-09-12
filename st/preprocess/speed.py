"""
This script add more information
to the KB_krant index, to speed up search
efficiency.
"""
from elasticsearch import Elasticsearch, RequestError, ConnectionError
from urllib import quote, unquote
import params as p
import argparse
import datetime
from Annotator import Annotator
import sys

es = Elasticsearch()
stat_field = 'text'

def add_document_length(docs):
    for d in docs:
        docid = d['_id']
        # Get term vector to compute doc length
        termvector = es.termvector(id=docid, index=p.INDEX, doc_type=p.DOC_TYPE, 
                fields=stat_field)
        term_stats = termvector['term_vectors'].get(stat_field, {}).get('terms', [])
        if term_stats == []:
            pass

        doc_length = sum([term_stats[t]['term_freq'] for t in term_stats])
        doc = {'doc':{'doclength': doc_length }}
        # Update the index
        es.update(index=p.INDEX, doc_type=p.DOC_TYPE, id=docid, body=doc)
        #print es.get_source(index=p.INDEX, doc_type=p.DOC_TYPE, id=docid).get('doclength')


def add_field(docs, field):
    if field == 'doclength':
        add_document_length(docs)

 
def process_documents(startyear, endyear, field):
    # First update mapping to add this field
    es.indices.put_mapping(index=p.INDEX, doc_type=p.DOC_TYPE, body=p.MAPPING)
 
    # Get documents
    qry = {
        'range': {
            'date': {
                'gte': '%s-01-01'%startyear,
                'lte': '%s-12-31'%endyear,
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
    docs = res['hits']['hits']
    add_field(docs, field)

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
        print "Add %s: %s - %s/%s"%(field, start, start+size, total)
        docs = res['hits']['hits']
        add_field(docs, field)
        start += size    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('startyear', 
        help="The starting year of the documents to be processed (yyyy)")
    parser.add_argument('endyear',
        help="The end year of the documents to be processed (yyyy)")
    parser.add_argument('field_to_add', 
        help="The added field name; options are: doclength")
    args = parser.parse_args()
    
    process_documents(args.startyear, args.endyear, args.field_to_add)

 
