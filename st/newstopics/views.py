from django.shortcuts import render, render_to_response, HttpResponse
from django.core.context_processors import csrf
from searchKBNews import KBNewsES
from st import settings
import simplejson as js
import itertools
import datetime
# Create your views here.



searcher = KBNewsES(settings.ES)

def index(request):
    c = csrf(request)
    template = 'newstopics/index.html'
    c['advanced_search_status'] = 'hidden'

    return render_to_response(template, c)


# URL version
def simple_search(request):
    c = {'advanced_search_status': 'hidden'}
    query = request.GET.get('q', '')
    
    # Set default values for the form
    if not query == '':
        simple_search_form = {'q': query}
        c['simple_search_form'] = simple_search_form

    template = 'newstopics/index.html'
    return render_to_response(template, c)

def advanced_search(request):
    print request.POST
    print request.GET
    c = {'advanced_search_status': ''}
    must = request.GET.get('must', '')
    mustnot = request.GET.get('mustnot', '')
    should = request.GET.get('should', '')

    # Set default values for the form
    advanced_search_form = {}
    if not must == '':
        advanced_search_form['must'] = must
    if not mustnot == '':
        advanced_search_form['mustnot'] = mustnot
    if not should == '':
        advanced_search_form['should'] = should 
    c['advanced_search_form'] = advanced_search_form

    template = 'newstopics/index.html'
    return render_to_response(template, c)

   


# Ajax version
def process_query(request):
    # Force csrf token to be set
    if request.is_ajax:
        data = {}

        # prameters for searching
        index = 'kb_krant'
        doc_type = 'article'
        fields = ['text', 'title']
        field = 'text'

        # search for keywords
        size = int(request.POST['page_size'])
        start = (int(request.POST['current_page']) - 1) * size 
        query = request.POST['query']
        res = searcher.keyword_search(index, doc_type, query, fields, size, start)
        if res['hits']['total'] > 0:
            print res['hits']['hits'][0]['_source'].keys()
            results = [{'docid': doc['_id'],
                    'url': 'http://resolver.kb.nl/resolve?urn=%s'%doc['_id'],
                    'title': '...'.join(doc['highlight']['title']),
                    'loc': doc['_source']['loc'],
                    'date': doc['_source']['date'],
                     # Get the summary of the results
                    'summary': '...'.join(doc['highlight']['text']),
                    'papertitle': doc['_source']['papertitle']

                } for doc in res['hits']['hits']] 

            data = {'results': results, 'total': res['hits']['total']}
        json_data = js.dumps(data)		
        response = HttpResponse(json_data, content_type="application/json")
    else:
        return render_to_response('errors/403.html')
    return response

def visualization(request):
    if request.is_ajax:
        data = {}

        # prameters for searching
        index = 'kb_krant'
        doc_type = 'article'
        fields = ['text', 'title']
        field = 'text'

        # search for keywords
        size = settings.SAMPLE_SIZE
        start = 0
        query = request.POST['query']

        res = searcher.keyword_search(index, doc_type, query, fields, size, start)
        # Get top concepts from this result set
        topConcepts = searcher.topConcepts(res, settings.NUM_TOPICS, cmethod=settings.CMETHOD)
        data['counts']= count_concepts(topConcepts)
        # normalize the scores between 15 and 70
        scores = [c[1] for c in topConcepts]
        
        scores = [(s-min(scores))/(max(scores)-min(scores)+1)*(70-15)+15
                for s in scores]
        data['concepts'] = [(topConcepts[i][0], scores[i]) 
                for i in range(len(scores))]
        json_data = js.dumps(data)		
        response = HttpResponse(json_data, content_type="application/json")
    else:
        print 'ERROR: not an ajax call'
        return render_to_response('errors/403.html')
    return response


def count_concepts(concepts):
    # count concepts by location and time
    counts = []
    if settings.DATE_GROUP_TYPE == 'year':
        entries = [(concept[0], c[0], c[1].split('-')[0]) 
            for concept in concepts 
            for c in concept[-1]]
    elif settings.DATE_GROUP_TYPE == 'month':
        entries = [(concept[0], c[0], c[1].rsplit('-', 1)[0]) 
            for concept in concepts 
            for c in concept[-1]]

    # group by location
    entries.sort(key=lambda x: x[1])
    for loc, group in itertools.groupby(entries, lambda x: x[1]):
        concepts = list([(g[0], g[2]) for g in group])   
        # group by concepts
        concepts.sort(key=lambda x: x[0])
        concept_counts = []
        for concept, group2 in itertools.groupby(concepts, lambda x: x[0]):
            # Group by dates
            dates = [g[1] for g in group2]
            dates.sort()
            date_counts = []
            for date, group3 in itertools.groupby(dates):
                date_counts.append((date, len(list(group3))))
            date_counts.sort(key=lambda x: x[0])    
            concept_counts.append((concept, date_counts))
        counts.append((loc, dict(concept_counts)))
    return dict(counts)

