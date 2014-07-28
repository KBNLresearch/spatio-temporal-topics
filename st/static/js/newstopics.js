//Global variables
var page_size = 10;
var current_page = 1;
var total_results = 0;

$(document).ready(function(){
    $('#search_submit').click(function(){
        var query = $('#searchbox').val();
        search_submit(query);
    });

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
            current_page = 1;
            //total_pages = Math.ceil(results.length/page_size);
            show_results();
        });
}

function show_results(){
    //show the results of the current page
    resultlist = [
            '<div class="info">',
            '# '+ total_results +' Results found.',
            '</div>',
        ];
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
}

function pagination(current_page){
    pagination = [];
    
}


