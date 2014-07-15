"""
Clean the GCLD, only keep the part
we need. Create a index for it.
"""
from bz2 import BZ2File
from collections import deque 
from elasticsearch import Elasticsearch, RequestError, ConnectionError
import params as p
import urllib
import sys

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
  
    # For inverted dictionary
    if es.indices.exists_type(index=p.INDEX_GCLD, doc_type=p.DOC_TYPE_INV_GCLD):
        print 'Doc type exists: ', p.DOC_TYPE_INV_GCLD
    else:
        print 'Create mapping for doc_type %s'%p.DOC_TYPE_INV_GCLD
        es.indices.put_mapping(index=p.INDEX_GCLD, doc_type=p.DOC_TYPE_INV_GCLD, body=p.MAPPING_INV_GCLD)
  
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


def index_dictionary(type_dictionary):
    if type_dictionary == 'dict':
        inputfile = p.PATH_GCLD
        doc_type = p.DOC_TYPE_GCLD

    elif type_dictionary == 'inv':
        inputfile = p.PATH_INV_GCLD
        doc_type = p.DOC_TYPE_INV_GCLD
    else:
        print 'Unrecognizable dictionary type'
        sys.exit()
    
    f = BZ2File(inputfile)
    docid = 0
    for c in f:
        if type_dictionary == 'dict':
            string, concept = c.split('\t')
            prob, url = concept.split(' ')[0:2]
        else:
            strs = c.split('\t')
            url = strs[0]
            string_raw = strs[1]
            strs = string_raw.split(' ')
            prob = strs[0]
            string = ' '.join(strs[1:])

        if string.strip() == '':
            continue
        if prob == '0':
            continue

        s = string.replace('_', ' ').replace('"', '').strip()
        string = string_to_unicode(s)
        url = string_to_unicode(url)        
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
        add_document('%s_%s'%(type_dictionary, docid), doc_type, document)
        if docid%10000 == 0:
            print docid
        docid += 1
    f.close()

def index_language_mapping():
    inputfile = p.PATH_LANG_MAP

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
    if len(sys.argv)<2:
        print 'Usage: python indexGCLD.py type'
        print 'options for type: [dict|inv|lang]'
        print '    dict: the dictionary'
        print '    inv: the inverted dictionary'
        print '    lang: mapping of Dutch language'
        sys.exit()

    # Create an index
    create_index()

    if sys.argv[1] == 'lang':
        print 'Indexing language map'
        #Parse and index the language mapping
        index_language_mapping()    

    else:
        print 'Indexing GCLD', sys.argv[1]
        # Parse and index the GCLD
        index_dictionary(sys.argv[1])



