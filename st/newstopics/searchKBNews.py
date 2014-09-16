"""
Interact with KB news index
Index content:
"""
from elasticsearch import Elasticsearch
import itertools as it
import re
from math import exp, log
from st import settings 
import operator

class KBNewsES(object):
    def __init__(self, es):
        """
        @params
        es: elasticsearch object, initialized
        """
        self.es = es

        # regular expression used:
        self.reg_prox_post = re.compile('~\d+')
        self.reg_exact = re.compile('".+?"')


    def search_news(self, index, doc_type, query, fields, size, start):
        """
        Search KB news and return a set of documents
        @params:
            index: index name
            doc_type: doc_type
            query: raw query, a dictionary
            field: array of the fields to be searched
            size: number of results
            start: start position of the results
        @ return
            res: retrieved results in ranked order        
        """   
        res = []
        processed_query = self.construct_query(query, fields)
        if processed_query == '':
            return res, -1
        qry = {
            'query': processed_query,

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
        print processed_query

        res = self.es.search(index=index, doc_type=doc_type, body=qry,
                size=size, from_=start, fields=settings.RET_FIELDS)
        #print res['hits']['hits'][0]['highlight']['text']

        total_results = res['hits']['total']
        docs = res['hits']['hits']

        # Prepare result list
        resultlist = [{} for i in range(len(docs))]
        for i in range(len(docs)):
            source = docs[i]['_source']
            highlights = docs[i]['highlight']
            result = {
                    'docid': docs[i]['_id'],
                    'url': 'http://resolver.kb.nl/resolve?urn=%s'%docs[i]['_id'],
                    'title': '...'.join(highlights['title']),
                    'loc': source['loc'],
                    'date': source['date'],
                     # Get the summary of the results
                    'summary': '...'.join(highlights['text']),
                    'papertitle': source['papertitle'],
                    'res_counter': i+1+start,
                    'doclength': source.get('doclength', 0)
                } 
            resultlist[i] = result
      
        return resultlist, total_results 

  
    def parse_query(self, string):
        """
        Parse query to get:
         - proxmity queries
         - exact phrases
         - wildcard in terms
        """ 
        # find exact phrases
        segments = []
        exac = self.reg_exact.search(string)
        while not exac == None: 
            # pre contains neither proximity or exact query
            pre = string[0:exac.start()].strip()
            if not pre == '':
                segments.append((pre, 'terms'))

            # matched may contain proximity query
            matched = string[exac.start():exac.end()].strip()
            post = string[exac.end():].strip()

            # Check proximity postfix
            prox_post = self.reg_prox_post.match(post)
            if prox_post == None:
                segments.append((matched, 'exact'))
            else:
                # proximity
                prox = string[exac.start(): exac.end()+prox_post.end()].strip()
                segments.append((prox, 'prox'))
                post = post[prox_post.end():].strip()
            # start new round
            string = post
            exac = self.reg_exact.search(string)
        if not string == '':
            segments.append((string, 'terms'))
        return segments

    def construct_query(self, raw_query, fields):
        """
        Construct query language based on the input keyword query
        @Params
        query: a dictionary, possible keys are: must, mustnot, should 
        fields: fields to search for
        """
        # Check if there phrases
        #query_terms = query.split('"')
        should = raw_query.get('should', '')
        must = raw_query.get('must', '')
        mustnot = raw_query.get('mustnot', '')
        time_period = raw_query.get('periods', '')
        newspapers = raw_query.get('newspapers', '')

        if should == '' and must == '' and mustnot == '':
            return ''
        # Construct the query part 
        query_bool = {}
        if not must == '':
            query_bool['must'] = {
                "query_string": {
                    'query': must,
                    "fields": fields
                },
            }
        if not mustnot == '':
             query_bool['must_not'] = {
                "query_string": {
                    'query': mustnot,
                    "fields": fields,
                }
            }
        if not should == '':
            query_bool['should'] = {
                "query_string": {
                    'query': should,
                    "fields": fields,
                }
            } 
        query_part = {'bool': query_bool}

        # Construct the filter part
        # time filters
        time_filter = {}
        if not time_period == '': 
            periods = [t.split('-') for t in time_period.split(';')]
            # conditions of ranges in "or" relation
            cond_periods = [{'range': 
                                {'date':
                                    {'gte': '%s-01-01'%p[0],
                                    'lte': '%s-12-31'%p[1],}
                                }
                            } for p in periods]
            if len(cond_periods) == 1:
                time_filter = cond_periods[0]
            elif len(cond_periods) > 1:
                time_filter = {'or': cond_periods}
            
        # newspaper title filters
        np_filter = {}
        if not newspapers == '':
            filter_query = 'OR'.join(['("%s")'%title 
                for title in newspapers.split(';')])  
            np_filter = {'query': 
                            {'query_string': 
                                {'query': filter_query, 
                                'fields': ['papertitle'],
                                }
                            }
                        }   
         
        # These two filters are 'and' relation
        filters = {}
        if time_filter == {} and np_filter == {}:
            filters = {}
        elif time_filter == {}:
            filters = np_filter
        elif np_filter == {}:
            filters = time_filter
        else:
            filters = {'and': [time_filter, np_filter]}
 
        query = {}
        if filters == {}:
            query = query_part 
        else:
            query['filtered'] = {
                'query': query_part,
                'filter': filters
            }
        return query


    def agg_newspaper_counts(self, index, doc_type):
        """
        Aggregate counts of articles per newspaper
        """
        body = {
                'aggs': {
                    'papercount': {
                        'terms': {
                            'field': 'papertitle',
                            'size': 0
                        },
                    }
                }
            }
        res = self.es.search(index=index, doc_type=doc_type, 
            body=body, search_type="count")
        newspapers = res['aggregations']['papercount']['buckets']
        return sorted([(p['key'][:70], p['doc_count']) for p in newspapers], key=operator.itemgetter(0))


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

        concepts = []
        for doc in docs:
            entities = doc['_source'].get('entity')
            if not entities == None:
                # filter concepts based on method and score
                entities = list(it.ifilter(lambda x: x.get('method', [])==cmethod, entities))
                concepts += [(doc, self.clean(e.get('concept', '')), e) 
                    for e in entities]

        #concepts = [(doc, self.clean(concept.get('concept', '')), concept)
        #    for doc in docs 
        #    for concept in doc.get('_source', {}).get('entity', {})]

        # for each concept, compute the score
        concept_score = []
        concepts.sort(key=lambda x: x[1])
        for k, g in it.groupby(concepts, lambda x:x[1]):
            g = list(g)
            if len(g) <= 2:
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
    
    query = {
            'filtered': {
                "filter": {
                    'and': [ {'or': {
                            'filters': [
                                {"range": {"date": {"gte": "1914-01-01", "lte": "1915-12-31"}}},
                                {"range": {"date": {"gte": "1916-01-01", "lte": "1918-12-31"}}},
                                ]}}, 
                        {'query': {
                            'query_string': {
                                'query': 'first world war',
                                'fields': fields
                            }
                        }
                        }
                    ]
                },
                'query': {
                    'bool': {
                        'must': {
                            'query_string': {
                                'query': "first w*rld #war",
                                'fields': fields 
                                }
                            },
                        'should': {
                            'query_string': {
                                    'query': '',
                                    'fields': fields
                                }
                            }
                        }
                    }
                }
            }
    qry = {'query': query}
    res = es.search(index=index, doc_type=doc_type, body=qry, size=10, from_=0)
    print res['hits']['total']
   # res = searcher.keyword_search(index, doc_type, query, fields, 1000, 0)
   # for doc in res['hits']['hits']:
   #     print doc['highlight']

    #print len(res['hits']['hits'])
  #  C = searcher.topConcepts(res, 20)
  #  for c in C:
  #      print c[0], c[1], len(c[2])


