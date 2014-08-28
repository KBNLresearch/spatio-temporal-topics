"""
Interact with KB news index
Index content:
"""
from elasticsearch import Elasticsearch
import itertools as it
import re
from math import exp, log

class KBNewsES(object):
    def __init__(self, es):
        """
        @params
        es: elasticsearch object, initialized
        """
        self.es = es

    def keyword_search(self, index, doc_type, query, fields, size, start):
        """
        Run a keyword search and return a set of documents
        @params:
            index: index name
            doc_type: doc_type
            query: keyword query
            field: array of the fields to be searched
            size: number of results
            start: start position of the results
        @ return
            res: retrieved results in ranked order        
        """    
        qry = {
            'query': {
                'multi_match': {
                    "query": query,
                    "fields": fields
                    }
                },
            'highlight': {
                'order': 'score',
                'pre_tags': ['<span class="highlight">'],
                'post_tags': ['</span>'],
                'fields': {
                    'title': {
                        'number_of_fragments': 1,
                        'no_match_size': 20},

                    'text': {
                        'fragment_size': 20,
                        'number_of_fragments': 1, 
                        },
                }    
            }
            }
        # Default only consider the top 1000 results
        res = self.es.search(index=index, doc_type=doc_type, body=qry,
                size=size, from_=start)
        return res


    def topConcepts(self, results, topX, cmethod="ner"):
        """
        Get top X concepts from a set of documents
        Scoring:        
            p(e|D) = sum_{d\in D}p(e|d)p(d)
            where 
                p(e|d) = \prod_{w \in e} p(w|d)
                p(d) = score(d)/C,  C: a normalization constant

            log(p(e|D))/log(p(e|C)) as measuring of 
            prominance of e in D

        @params:
            results: the set of retrieved docs
            topX: the number of top concepts to return
            cmethod: filter on the method that generates 
                the concepts, default: ner

        @return:
            concepts: the set of selected concepts  
        """        
        # Collect concepts
        docs = results['hits']['hits']
        doc_rank = dict([(docs[i]['_id'], i) for i in range(len(docs))])

        concepts = [(doc, self.clean(concept.get('concept', '')), concept)
            for doc in docs 
            for concept in doc['_source'].get('entity', {})]
        for doc in docs:
            print doc

        # filter concepts based on method and score
        concepts = list(it.ifilter(lambda x: x[2].get('method', [])==cmethod, concepts))

        # for each concept, compute the score
        concept_score = []
        concepts.sort(key=lambda x: x[1])
        for k, g in it.groupby(concepts, lambda x:x[1]):
            g = list(g)
            if len(g) <= 5:
                continue
            docs = [(gg[0]['_source']['loc'], gg[0]['_source']['date']) for gg in g]
            # p(e|D) \propto \sum_{w \in e} exp(log p(e|d) + log(d))
            p_e_D = log(sum([exp(gg[2]['doc_score']+gg[0]['_score']) for gg in g]))

            p_e_C = sum([gg[2]['col_score'] for gg in g])
            
            # score = log(p(e|D)) - log(p(e|C))
            score = p_e_D - p_e_C 
            concept_score.append((k, score, docs)) 
        concept_score.sort(key=(lambda x: x[1]), reverse=True)
        
        return concept_score[0:topX]

         
    def normalize(self, string, index, field):
        tokens = self.es.indices.analyze(index=index, field=field, text=string)
        return ' '.join(tokens) 

    def clean(self, string):
        return re.sub(r'\W+', ' ', string).strip()

if __name__ == '__main__':
# Test
    es = Elasticsearch()
    searcher = KBNewsES(es)
    index = 'kb_krant'
    doc_type = 'article'
    query = 'Trotsky'
    fields = ['text', 'title']
    field = 'text'
    res = searcher.keyword_search(index, doc_type, query, fields, 1000, 0)
    for doc in res['hits']['hits']:
        print doc['highlight']

    #print len(res['hits']['hits'])
    C = searcher.topConcepts(res, 20)
    for c in C:
        print c[0], c[1], len(c[2])


