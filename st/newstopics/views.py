from django.shortcuts import render, render_to_response, HttpResponse
from django.core.context_processors import csrf
from searchKBNews import KBNewsES
from st import settings
import simplejson as js
import itertools
import datetime
import math
# Create your views here.
from elasticsearch import Elasticsearch


ES = Elasticsearch(
    max_retries = 10,
    keepAlive = True,
    maxSockets = 100,
    minSockets = 1,
)
searcher = KBNewsES(ES)
sort_options = {
    '': 'Relevance',
    'date': 'Date',
    'doclength': 'Article length',
#    'page': 'Newspaper page',
}

def index(request):
    c = csrf(request)
    template = 'newstopics/index.html'
    c['advanced_search_status'] = 'hidden'
    c['pagination'] = {'left_most_hidden': 'hidden', 'right_most_hidden': 'hidden'}
    c['newspaper_counts'] = searcher.agg_newspaper_counts(settings.INDEX, settings.DOC_TYPE)
    c['selected_newspapers'] = js.dumps(dict([(loc['id'],[]) for loc in c['newspaper_counts']]))
    c['retrieval_status'] = 'hidden'
    request.session['newspaper_counts'] = c['newspaper_counts']

    c['current_query'] = {
            'mode': 'simple',
            'query': js.dumps({}),
        } 
    
    return render_to_response(template, c)

# URL version
def simple_search(request):
    c = {}
    c.update(csrf(request))

    # this is a simple search
    c['advanced_search_status'] = 'hidden'

    # Set contextual parameter values
    c['newspaper_counts'] = request.session['newspaper_counts']
    if c['newspaper_counts'] == None:
        c['newspaper_counts'] = searcher.agg_newspaper_counts(settings.INDEX, settings.DOC_TYPE)
        request.session['newspaper_counts'] = c['newspaper_counts']
    c['selected_newspapers'] = js.dumps(dict([(loc['id'],[]) for loc in c['newspaper_counts']]))
 
    # Process request
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', '')
    current_page = request.GET.get('page', 1)
    current_page = 1 if current_page == '' else int(current_page)

    raw_query = {
        'should': query,
        'sort': sort,
    }
    # Contextual parameters passed to UI
    # Context of search form
    if not query == '':
        simple_search_form = {'q': query}
        c['simple_search_form'] = simple_search_form

    # Context of result list
    c['resultlist'], count = searcher.search_news(
            settings.INDEX,
            settings.DOC_TYPE,
            raw_query,
            settings.SEARCH_FIELDS,
            settings.PAGE_SIZE,
            (current_page-1)*settings.PAGE_SIZE) 

    if count == -1:
        c['total_results'] = ''
        c['retrieval_status'] = 'hidden'
    else:
        c['total_results'] = '#%s results found'%count

    # Context of reulst operation
    # get the sorting name for the selected sorting type
    c['result_sort'] = {'type': sort, 'name': sort_options[sort]} 

    # Context of pagiation
    c['pagination'] = make_pagination(count, current_page) 

    # Context of current query 
    c['current_query'] = {
            'mode': 'simple',
            'query': js.dumps(raw_query),
        } 
    # Return the results
    template = 'newstopics/index.html'
    return render_to_response(template, c)

def advanced_search(request):
    #print 'advanced search'
    c = {}
    c.update(csrf(request))

    # Process request
    must = request.GET.get('must', '')
    mustnot = request.GET.get('mustnot', '')
    should = request.GET.get('should', '')
    periods = request.GET.get('periods', '')
    sort = request.GET.get('sort', '')

    current_page = request.GET.get('page', 1)
    current_page = 1 if current_page == '' else int(current_page)

    # Process request - Context of available newspapers
    c['newspaper_counts'] = request.session['newspaper_counts']
    if c['newspaper_counts'] == None:
        c['newspaper_counts'] = searcher.agg_newspaper_counts(settings.INDEX, settings.DOC_TYPE)
        request.session['newspaper_counts'] = c['newspaper_counts']


    # Process request - Get newspaper selections
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
    #print len(selected_papers), len(all_news)
    if len(selected_papers) == len(all_news):
        selected_papers = ''
    elif len(selected_papers) == 0:
        selected_papers = 'none'  

    # Search query 
    raw_query = {'should': should, 'must': must, 'mustnot': mustnot,
                'periods': periods,
                'newspapers': selected_papers,
                'sort': sort,
                }

    # Context parameters passed to UI 

    # Context of advanced search box 
    c ['advanced_search_status'] = ''

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

    # Context of result list
    c['resultlist'], count = searcher.search_news(
            settings.INDEX,
            settings.DOC_TYPE,
            raw_query,
            settings.SEARCH_FIELDS,
            settings.PAGE_SIZE,
            (current_page-1)*settings.PAGE_SIZE) 

    if count == -1:
        c['total_results'] = ''
        c['retrieval_status'] = 'hidden'
    else:
        c['total_results'] = '#%s results found'%count

    # Context of pagination
    c['pagination'] = make_pagination(count, current_page) 
   
    # Context of result operation
    c['result_sort'] = {'name': sort_options[sort], 'type': sort}

    # In case we want to show the current query 
    c['current_query'] = {
            'mode': 'advanced',
            'query': js.dumps(raw_query),
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

def vis_termclouds(request):
    if request.is_ajax:
        data = {}

        # prameters for searching
        index = 'kb_krant'
        doc_type = 'article'
        field = request.POST.get('cloud_type', 'text') 

        fields = ['text', 'title']
        changed_loc_id = int(request.POST.get('changed_loc_id'))
        query = {
            'must': request.POST.get('must', ''),
            'mustnot': request.POST.get('mustnot', ''),
            'should' : request.POST.get('should', ''),
            'periods' : request.POST.get('periods', ''),
            'newspapers': {}
        }
        term_clouds = {}
        papers = {}
        # loop over np types (location)
        # for np in request.session['newspaper_counts']:

        # get the newspaper selection that have been updated
        np = request.session['newspaper_counts'][changed_loc_id]
        select = request.POST.getlist('newspapers_%s'%changed_loc_id)
        print request.POST 
        print changed_loc_id
        print select
        if select[0] == '' or select[0] == 'all':
            query['newspapers'] = [x[0] for x in np['news']]
            papers = 'All'
            tc = searcher.term_clouds(index, doc_type, field, query, fields, 10)
            print 'all'

        elif select[0] == 'none':
            papers = 'None'
            tc = []
            print 'none'
        else:
            query['newspapers'] = [np['news'][int(x.split('_')[-1])][0] 
                    for x in select[0].split(';')]
            papers = '; '.join(query['newspapers']) 
            tc = searcher.term_clouds(index, doc_type, field, query, fields, 10)
            print 'something'
        data['tc'] = tc
        data['papers'] = papers
        data['year'] = request.POST['year']
        data['loc_id'] = changed_loc_id
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

