"""
Clean the GCLD, only keep the part
we need. Create a index for it.
"""
from bz2 import BZ2File
from collections import deque 
from elasticsearch import Elasticsearch, RequestError, ConnectionError
import params as p
import urllib

es = Elasticsearch()

def create_index():
    """
        Create index and put mapping of document structure. 
        If the index for the given name exists, skip it. 
    """
    # Check if the index already exists
    if es.indices.exists(index=p.INDEX_GCLD):
        print 'Index %s exists'%p.INDEX_GCLD
    else:
        print 'Creat index %s'%p.INDEX_GCLD
        es.indices.create(index=p.INDEX_GCLD)

    # Creat document types
    # For dictionary
    if es.indices.exists_type(index=p.INDEX_GCLD, doc_type=p.DOC_TYPE_GCLD):
        print 'Doc type exists: ', p.DOC_TYPE_GCLD
    else:
        print 'Create mapping for doc_type %s'%p.DOC_TYPE_GCLD
        es.indices.put_mapping(index=p.INDEX_GCLD, doc_type=p.DOC_TYPE_GCLD, body=p.MAPPING_GCLD)
   
    # For language mapping 
    if es.indices.exists_type(index=p.INDEX_GCLD, doc_type=p.DOC_TYPE_LANG):
        print 'Doc type exists: ', p.DOC_TYPE_LANG
    else:
        print 'Create mapping for doc_type %s'%p.DOC_TYPE_LANG
        es.indices.put_mapping(index=p.INDEX_GCLD, doc_type=p.DOC_TYPE_LANG, body=p.MAPPING_LANG)


def add_document(doc_id, doctype, document):
    """
        Add document to index
        Parameters:
        * document: a json object
    """
    es.index(index=p.INDEX_GCLD, doc_type=doctype, body=document, id=str(doc_id))

def string_to_unicode(string):
    try:
        return unicode(string)
    except:
        for e in ['utf-8', 'latin-1']:
            try:
                return unicode(string, e)
            except:
                pass  
    return None


def index_dictionary(inputfile):
    f = BZ2File(inputfile)
    docid = 0
    for c in f:
        string, target = c.split('\t')
        if string.strip() == '':
            continue
        prob, u = target.split(' ')[0:2]
        if prob == '0':
            continue
        s = string.replace('_', ' ').strip()
        string = string_to_unicode(s)
        url = string_to_unicode(u)        
        if string == None:
            print 'Encoding problem: %s'%s
            sys.exit()
        if url == None:
            print 'Encoding problem: %s'%u
            sys.exit()

        # Make a document
        document = {
            'string': string,
            'concept': url.strip(),
            'score': prob.strip(),
        }
        # add to index
        add_document('gcld_%s'%docid, p.DOC_TYPE_GCLD, document)
        if docid%10000 == 0:
            print docid
        docid += 1
    f.close()

def index_language_mapping(inputfile):
    f = BZ2File(inputfile)
    docid = 0
    for c in f:
        s, t = c.strip().split('\t')
        start = string_to_unicode(s)
        target = string_to_unicode(t) 
        if start == None:
            print 'Encoding problem: %s'%start
            sys.exit()
        if target == None:
            print 'Encoding problem: %s'%target        
            sys.exit()

        document = {
            'from': start,
            'to': target
        }
        add_document('lang_%s'%docid, p.DOC_TYPE_LANG, document)

        if docid%1000 == 0:
            print docid
        docid += 1

if __name__ == '__main__':
    # Create an index
    create_index()

    print 'Indexing language map'
    #Parse and index the language mapping
    index_language_mapping(p.PATH_LANG_MAP)    

    print 'Indexing GCLD'
    # Parse and index the GCLD    
    index_dictionary(p.PATH_GCLD)



