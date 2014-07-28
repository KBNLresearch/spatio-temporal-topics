from django.shortcuts import render, render_to_response, HttpResponse
from django.core.context_processors import csrf
from searchKBNews import KBNewsES
from st import settings
import simplejson as js
# Create your views here.

searcher = KBNewsES(settings.ES)
snippet_size = 20

def index(request):
    c = csrf(request)
    template = 'newstopics/index.html'
    return render_to_response(template, c)


def process_query(request):
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
            results = [{'docid': doc['_id'],
                    'url': 'http://resolver.kb.nl/resolve?urn=%s'%doc['_id'],
                    'title': '...'.join(doc['highlight']['title']),
                    'loc': doc['_source']['loc'],
                    'date': doc['_source']['date'],
                     # Get the summary of the results
                    'summary': '...'.join(doc['highlight']['text']),

                } for doc in res['hits']['hits']] 

            data = {'results': results, 'total': res['hits']['total']}
        json_data = js.dumps(data)		
        response = HttpResponse(json_data, content_type="application/json")
    else:
        return render_to_response('errors/403.html')
    return response

   
