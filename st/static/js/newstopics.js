//Global variables
var page_size = 10;
var current_page = 1;
var total_results = 0;
var total_pages = 0;
var start_page = 1;
var end_page = 1;
var current_query = ''

$(document).ready(function(){

//Sumit a query and get results    
$('#search_submit').click(function(){
    var query = $('#searchbox').val();
    current_page = 1;
    current_query = query;
    search_submit(query);
});

//Click on pagination

//Click on shifting paginaiton
$('#pagination').on('click', '#left_pager', function(){
    //move the current page to next
    current_page = current_page - 1;
    search_submit(current_query);     
});

$('#pagination').on('click', '#right_pager', function(){
    current_page = current_page + 1;
    search_submit(current_query);
});

//Click on filtering

//load visualisation

});

function search_submit(query){
	 $.ajax({
           	type: "POST",
            url: url_process_query,
            data: {
			    query: query,
                page_size: page_size,
                current_page: current_page
                
            }
        }).done(function(response) {
            results = response['results'];
            total_results = response['total']; 
            total_pages = Math.ceil(total_results/page_size);
            //pagination
            show_results();

            $(window).scrollTop($('#result_top').offset().top-100);
        });
}

function show_results(){
    //show the results of the current page
    resulttop = [
            '<div class="info">',
            '# '+ total_results +' Results found.',
            '</div>',
        ];
    $('#result_top').html(resulttop.join(''))
    resultlist = []
    for (var i = 0; i<results.length; i++){
        //Make the meta information
        meta = [
            '<div class="metainfo">',
            results[i]['date'],
            ';  ',
            results[i]['loc'], 
            '</div>'
        ]
        //Make the snippet
        snippet = [
            '<a class="list-group-item" ', 
            'target="_blank" href="',
            results[i]['url'], 
            '">',
            '<div class="restitle">',
            results[i]['title'],
            '</div>',
            meta.join(''),
            '<div class="list-group-item-text">',
            results[i]['summary'],
            '</div>',
            '</a>',
            '</div>',
        ]
        resultlist.push(snippet.join(''));
    }

    $('#resultlist').html(resultlist.join(''));

    //make pagination
    pages = pagination();
    $('#pagination').html(pages);
}

function pagination(){
    console.log(current_page); 
    start_page = Math.max(1, current_page-3);
    end_page = Math.min(start_page+6, total_pages);

    var p = ['<ul class="pagination pagination-sm">'];
    //shift pagination backward
    if (start_page > 1){
        p.push('<li id="left_pager"><a class="pager">&laquo;</a></li>');
    }
    //pages    
    for (var i = start_page; i <= end_page; i++){
        var active = '';
        if (i == current_page)
            active = 'class="active"'
        item = [
            '<li id="page_' + i + '" ',
            active,
            '>',
            '<a class="pager">' + i + '</a>',
            '</li>'
            ]
        p.push(item.join(''));
    }
    //shift pagination forward
    if (end_page < total_pages){
        p.push('<li id="right_pager"><a class="pager">&raquo;</a></li>');
    }
    p.push('</ul>');
    return p.join(''); 
}


