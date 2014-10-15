"""
Annoate a news article with concepts  
"""
import requests 
import sys
import params as p
from elasticsearch import Elasticsearch
import xml.etree.ElementTree as et 
from string_util import html_unescape, string_to_unicode
from numpy import log, array

class Annotator(object):

    def __init__(self, method, field='_all'):
        """
        Initilizaiton
        @ Params: 
        method: the method used to annotate concepts
        indexclient: client for access an ES index
        field: the field for computing statistics, default '_all'
        """
        self.method = method
        self.es = Elasticsearch() 
        self.field = field


    def annotate(self, docid):
        if self.method == 'ner':
            persons, locs, orgs, others = self.get_NERs(docid)
            self.scoring(persons, docid)
            self.scoring(orgs, docid)
            self.scoring(locs, docid)
            self.scoring(others, docid)


            # Part of the doc to be updated
            doc = {
                'doc':{
                    'entity_person': persons,
                    'entity_location': locs,
                    'entity_organization': orgs,
                    'entity_other': others,  
                }
            }

        else:
            print 'The specifiied annotation method is not available: %s'%self.method

        # Update the index
        self.es.update(index=p.INDEX, doc_type=p.DOC_TYPE, id=docid, body=doc)
        #doc = self.es.get(index=p.INDEX, doc_type=p.DOC_TYPE, id=docid )



    def get_NERs(self, docid):
        url = 'http://tomcat.kbresearch.nl/tpta2/analyse?'
        params = {
            'url': 'http://resolver.kb.nl/resolve?urn=%s:ocr'%docid
            }
        # Get the metadata of the result set
        r = requests.get(url, params=self.encode_params(params))
        try:
            root = et.fromstring(r.content)
        except:
            print 'ERROR: Can not parse xml: %s'%docid
            return [], [], [], []
 
        ner = root.find('entities')
        persons, orgs, locs, others = [], [], [], [] 
        if not ner == None:
            ner = list(set([(entity.tag, entity.text) for entity in ner]))
            for entity in ner:
                concept = html_unescape(string_to_unicode(entity[1]))
                entry = {
                    'concept': concept,
                    'score': 0,
                    'doc_score': 0,
                    'col_score': 0,
                    }
                if entity[0] == 'person':
                    persons.append(entry)
                elif entity[0] == 'location':
                    locs.append(entry)
                elif entity[0] == 'organisation':
                    orgs.append(entry)
                else:
                    others.append(entry)

        return persons, locs, orgs, others 


    def scoring(self, annotations, docid):
        """
        compute the p(e|d) for each entity given a document
        """
        termvector = self.es.termvector(index=p.INDEX, 
            doc_type=p.DOC_TYPE, 
            id=docid,
            term_statistics=True,
            fields=self.field
            )
        # If we don't find the term, it should at least occured once
        total_term_counts = termvector['term_vectors'].get(self.field, {}).get('field_statistics', {}).get('sum_ttf', 1)

        # Get document level statistics
        term_stats = termvector['term_vectors'].get(self.field, {}).get('terms', [])
        if term_stats == []:
            pass
        doc_length = sum([term_stats[t]['term_freq'] for t in term_stats])
        # For each concept, compute score
        scored = []
        for a in annotations:
            tokens = self.es.indices.analyze(index=p.INDEX, field=self.field, text="%s"%a['concept'])
            terms = [t['token'] for t in tokens['tokens']]

            # Note: this term the term is not found, set it to count 1, as it must
            #   have occurred at least once.

            # p(w|d) = term_freq/doc_length
            p_w_d = array([float(term_stats.get(t, {}).get('term_freq', 1))/float(doc_length)
                    for t in terms])
            # p(w|C) = ttf/sum_ttf
            p_w_C = array([float(term_stats.get(t, {}).get('ttf', 1))/float(total_term_counts) 
                    for t in terms])
            a['doc_score'] = sum(log(p_w_d))
            a['col_score'] =  sum(log(p_w_C))

    # Requests encode the urls in a strange way
    # we encode it in our way here
    def encode_params(self, params):
        """
        Format the SRU retrieval parameters as url
        Parameters:
        * params: the SRU parameters stored in a dictionary 
        """
        return '&'.join(['%s=%s'%(key, params[key]) for key in params])


