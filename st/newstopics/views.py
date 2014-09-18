from django.shortcuts import render, render_to_response, HttpResponse
from django.core.context_processors import csrf
from searchKBNews import KBNewsES
from st import settings
import simplejson as js
import itertools
import datetime
import math
# Create your views here.



searcher = KBNewsES(settings.ES)

def index(request):
    c = csrf(request)
    template = 'newstopics/index.html'
    c['advanced_search_status'] = 'hidden'
    c['pagination'] = {'left_most_hidden': 'hidden', 'right_most_hidden': 'hidden'}
    c['newspaper_counts'] = searcher.agg_newspaper_counts(settings.INDEX, settings.DOC_TYPE)
    c['selected_newspapers'] = js.dumps(dict([(loc['id'],[]) for loc in c['newspaper_counts']]))
    request.session['newspaper_counts'] = c['newspaper_counts']
     
    return render_to_response(template, c)

# URL version
def simple_search(request):
    c = {}
    c.update(csrf(request))
    # Set contextual parameter values
    c['newspaper_counts'] = request.session['newspaper_counts']
    if c['newspaper_counts'] == None:
        c['newspaper_counts'] = searcher.agg_newspaper_counts(settings.INDEX, settings.DOC_TYPE)
        request.session['newspaper_counts'] = c['newspaper_counts']
    c['selected_newspapers'] = js.dumps(dict([(loc['id'],[]) for loc in c['newspaper_counts']]))
 
    # this is a simple search
    c['advanced_search_status'] = 'hidden'

    # Process request
    query = request.GET.get('q', '')
    current_page = request.GET.get('page', 1)
    current_page = 1 if current_page == '' else int(current_page)

    # Contextual parameters passed to UI
    if not query == '':
        simple_search_form = {'q': query}
        c['simple_search_form'] = simple_search_form

    raw_query = {'should': query}
    c['resultlist'], count = searcher.search_news(
            settings.INDEX,
            settings.DOC_TYPE,
            raw_query,
            settings.SEARCH_FIELDS,
            settings.PAGE_SIZE,
            (current_page-1)*settings.PAGE_SIZE) 


    if count == -1:
        c['total_results'] = ''
    else:
        c['total_results'] = '#%s results found'%count

    c['pagination'] = make_pagination(count, current_page) 

    c['current_query'] = {
            'mode': 'simple',
            'query': query,
        }   
    # Return the results
    template = 'newstopics/index.html'
    return render_to_response(template, c)

def advanced_search(request):
    print 'advanced search'
    c = {}
    c.update(csrf(request))

    # Context parameters passed to UI 
    c['newspaper_counts'] = request.session['newspaper_counts']
    if c['newspaper_counts'] == None:
        c['newspaper_counts'] = searcher.agg_newspaper_counts(settings.INDEX, settings.DOC_TYPE)
        request.session['newspaper_counts'] = c['newspaper_counts']

    # Set advanced search box visible
    c ['advanced_search_status'] = ''

    # Process request
    must = request.GET.get('must', '')
    mustnot = request.GET.get('mustnot', '')
    should = request.GET.get('should', '')
    periods = request.GET.get('periods', '')
    print periods
    # get newspaper selections
    news_selection = {}
    selected_papers = []
    all_news = sorted(list([s[0] for np in c['newspaper_counts'] for s in np['news']]))
    for np in c['newspaper_counts']:
        id_map = dict([(p[0], p[2]) for p in np['news']])
        selected_names = [name for name in request.GET.getlist('select_np_%s'%np['id'])]
        # to show in UI
        news_selection[np['id']] = selected_names
        # to query 
        if selected_names == ['All'] or selected_names == []:
            selected_papers += [s[0] for s in np['news']]
        elif selected_names == ['None']:
            pass
        else:
            selected_papers += selected_names
    selected_papers = sorted(list(set(selected_papers)))
    if len(selected_papers) == len(all_news):
        selected_papers = ''
    elif len(selected_papers) == 0:
        selected_papers = 'none'  

    current_page = request.GET.get('page', 1)
    current_page = 1 if current_page == '' else int(current_page)

    # Set default values for the form
    advanced_search_form = {}
    if not must == '':
        advanced_search_form['must'] = must
    if not mustnot == '':
        advanced_search_form['mustnot'] = mustnot
    if not should == '':
        advanced_search_form['should'] = should 
    if not periods == '':
        advanced_search_form['periods'] = periods
    c['selected_newspapers'] = js.dumps(news_selection)

    c['advanced_search_form'] = advanced_search_form

    # Perform search
    raw_query = {'should': should, 'must': must, 'mustnot': mustnot,
                'periods': periods,
                'newspapers': selected_papers,
                }

    c['resultlist'], count = searcher.search_news(
            settings.INDEX,
            settings.DOC_TYPE,
            raw_query,
            settings.SEARCH_FIELDS,
            settings.PAGE_SIZE,
            (current_page-1)*settings.PAGE_SIZE) 


    if count == -1:
        c['total_results'] = ''
    else:
        c['total_results'] = '#%s results found'%count

    c['pagination'] = make_pagination(count, current_page) 
   
    # In case we want to show the current query 
    c['current_query'] = {
            'mode': 'advanced',
            'query': 'MUST: %s; SHOULD: %s; MUSTNOT: %s'%(should, must, mustnot),
            'periods': 'PERIODS: %s'%periods,
            'newspapers': 'NEWSPAPERS: %s'%''
        }

    template = 'newstopics/index.html'
    return render_to_response(template, c)


def make_pagination(count, current_page):
    num_pages = int(math.ceil(float(count)/float(settings.PAGE_SIZE)))
    left_most = max(current_page-3, 1)
    right_most = min(current_page+6, num_pages)

    left_most_hidden, right_most_hidden = '', ''
    if left_most == 1:
        left_most_hidden = 'hidden'
    if right_most == num_pages:
        right_most_hidden = 'hidden'
    
    pages = []
    for i in range(left_most, right_most+1):
        page_active = ''  
        if i == current_page:
            page_active = 'active'
        pages.append({
                'page_id':i,
                'page_active': page_active,
            })

    pagination = {
            'num_pages': num_pages,
            'current_page': current_page,
            'left_most': left_most,
            'right_most':right_most,
            'left_most_hidden': left_most_hidden,
            'right_most_hidden': right_most_hidden,
            'pages': pages
             }
    return pagination


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

