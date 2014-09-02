//Global variables
var page_size = 10;
var current_page = 1;
var total_results = 0;
var total_pages = 0;
var start_page = 1;
var end_page = 1;
var current_query = ''
var colormap = {};

$(document).ready(function(){

//Sumit a query and get results
//then make visualisation
$('#search_submit').click(function(){
    var query = $('#searchbox').val();
    current_page = 1;
    current_query = query;
    search_submit(query);

    // Do visualization    
    visualize(query);
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

});

/*
function load_visualization(query){
	 $.ajax({
           	type: "POST",
            url: url_visualization,
            data: {
			    query: query,
            }
        }).done(function(response) {
            color_code = make_legends(response['concepts']);
            visualize(response['counts'], color_code);
        });

}
*/
function search_submit(query){
	 $.ajax({
           	type: "POST",
            url: url_process_query,
            data: {
			    query: query,
                page_size: page_size,
                current_page: current_page,
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
            results[i]['papertitle'],
            ';  ',
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
    //console.log(current_page); 
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

function visualize(query){
    // Get the locations to be visualized
    $('#vis_loc_summary').children().each(function(){
        loc = $(this).attr('id');
        //process this location
        vis_location_summary(query, loc);
    });
}

function vis_location_summary(query, loc){
	 $.ajax({
           	type: "POST",
            url: url_visualization,
            data: {
			    query: query,
                loc: loc,
            }
        }).done(function(response) {
        });

}

/*
function make_legends(concepts){
    legend = []
    colors = {} 
    for (var i in concepts){
        var concept = concepts[i][0];
        var score = Math.round(concepts[i][1]);
        var id = 'id="concept_'+concept+'" ';
        var fontsize = 'font-size:'+ score +'px';
        var color = getRandomColor();
        var style = 'style="color:'+ color +';'+fontsize+'" ';

        colors[concept] = colors;

        legend.push('<span ' + id + style + 'class="concept">');
        legend.push(concept);
        legend.push('</span>');
    }
    $('#legends').html(legend.join('\n'));
    return colors;
}

//input: data in the format of {loc: {concept: [[date, count]...]}}
//color_code: {concept: color}
function visualize(data, color_code){
    vis = []
    var i = 0
    for (loc in data){
        vis.push('<div id="loc_'+loc+'" class="location">');
        vis.push(loc);
        vis.push('<div id="vis_'+i+'" class="vis_location">');

        //add temporary content
        tmp = []
        for (concept in data[loc]){
            tmp.push('<p>');
            tmp.push(concept+': '+data[loc][concept]);
            tmp.push('</p>'); 
        }
        vis.push(tmp.join(''));

        vis.push('</div>')
        vis.push('</div>');
    }
    $('#visualization').html(vis.join('\n'));

    var id = 'vis_i' + i;
    draw_timeline(id, data[loc], color_code);
    i = i + 1;
}
*/
function getRandomColor() {
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}







