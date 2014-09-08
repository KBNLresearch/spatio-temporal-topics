//Global variables
var page_size = 10;
var current_page = 1;
var total_results = 0;
var total_pages = 0;
var start_page = 1;
var end_page = 1;
var current_query = ''
var colormap = [];

//store selected time periods
//using start as key
var current_periods_start = {};
//using end as key
var current_periods_end = {};

var current_periods = []; 

$(document).ready(function(){

//=========== Query operations ==================
// Operations related to submit and specify
// search request. 
//================================================

//Advanced_search: turn on/off the option
$('#advanced_option').click(function(){
    $('#advance_search').toggleClass('hidden');       
});

//Advanced search: Open/close query language instruction
$('#advanced_searchbox_learn').click(function(){
    $('#advanced_searchbox_info').toggleClass('hidden');
});
//Advanced search: Dismiss the query language instruction
$('#advanced_searchbox_hideinfo').click(function(){
    $('#advanced_searchbox_info').toggleClass('hidden');
});

//Advanced_search: add time period
$('#btn_add_period').click(function(){
    //Get the filled in years
    var start = $('#period_start').val();
    var end = $('#period_end').val();

    if (check_year(start, end)){
        //check its relation to existing periods
        var exists = current_periods.filter(function(d){
            return d[0] == start && d[1] == end;
        });
        //If already exists, do nothing
        if (exists.length == 0){
            //Check if it's covered by an existing period
            var covered = current_periods.filter(function(d){
                return d[0] <= start && d[1] >= end;
            });
            //Check if it covers an existing period
            var cover = current_periods.filter(function(d){
                return d[0] >= start && d[1] <= end; 
            });
            
            //If it doesn't covered or is covered by existing periods
            if (covered.length == 0 && cover.length == 0){
                //Add the period to existing periods
                var id = current_periods.length;
                current_periods.push([start, end, id]);
                //Show selected period
                show_selected_period(start, end);
            }
            else if (covered.length > 0){
                warn_coverage([start, end], covered[0], 'covered');
            }
            else if (cover.length > 0){
                warn_coverage([start, end], cover[0], 'cover');
            }
            //Set the hidden input values
            set_selected_values();
        }
    }
});


/*
//Sumit a query and get result then make visualisation
$('#search_submit').click(function(){
    var query = $('#searchbox').val();
    current_page = 1;
    current_query = query;
    search_submit(query);

    // Do visualization    
    visualize(query);
});
*/
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

/*========== Functions =================*/


// ======= Query operations ===============
//  Functions related to query operations
// ========================================

//Check the input time period
function check_year(start, end) {
    if (start == '' || end == '')
        return false //do nothing

    err1 = 'Error: Input should be a 4-digit number between 1914 and 1940, inclusive.'
    err2 = 'Error: The starting year should not be later than the ending year.'

    var syear = parseInt(start);
    var eyear = parseInt(end);

    valid = true 
    if (syear < 1914 || syear > 1940){
        valid = false
        //set element focus    
        $('#period_start').focus();
        //set error msg
        $('#period_err').text(err1);
    }
    else if (eyear < 1914 || eyear > 1940){
        valid = false
        //set element focus    
        $('#period_end').focus();
        //set error msg
        $('#period_err').text(err1);
    }
    else if (syear > eyear){
        valid = false
        $('#period_end').focus();
        $('#period_err').text(err2)
    }
    if (valid)    
        $('#period_err').text('');
    return valid;
}

function show_selected_period(start, end){
    var added = []
    for (var i = 0; i<current_periods.length; i++){
        if (current_periods[i] == '')
            continue
        var ele = [ 
            '<span class="period_label" id="period_'+i+'">',
            current_periods[i][0] + '-' + current_periods[i][1],
            '<span class="remove_period" id="remove_period_'+i+'"><sup>&times;</sup>',
            '</span>',
            '</span>'];
        added.push(ele.join('\n'));
    } //End showing element

    $('#div_selected_periods').html(added.join('\n'));
            
    //bind listener to the newly added periods
    $('#div_selected_periods').on('click', '.remove_period', function(){
    // Remove the selected element
    var id = $(this).attr('id').replace('remove_', '');
    $('#'+id).remove();
    // Set the element in the array empty  
    var idx = id.replace('period_', '');
        current_periods[idx] = '';
    }); //End binding 
}

function warn_coverage(newperiod, exist_period, type){
    //Show warning a new period covers or is covered
    // by an existing period
    var content = ['<div class="alert alert-warning" role="alert">'];
    if (type == 'covered')
        content.push(['This period is covered by period ', 
             exist_period[0]+'-'+exist_period[1] + '.',
             'Please select the period you want to keep:<br/>',
            ].join(' '));
    else if (type == 'cover')
        content.push(['This period covers period',
             exist_period[0] +'-'+ exist_period[1]+'.',
             'Please select the period you want to keep:<br/>',
            ].join(' '));
    
    content.push('<button type="button" class="btn btn-default" id="new_period">'
        +newperiod[0]+'-'+newperiod[1]+'</button>');
    content.push('<button type="button" class="btn btn-default" id="old_period">'
        +exist_period[0]+'-'+exist_period[1]+'</button>');
    content.push('</div>');
    //Show a alert for warning
    $('#period_err').html(content.join(' '));
    //Bind listener to the button in the error msg 
    $('#period_err').on('click', '#new_period', function(){
        console.log('new');
    });
    $('#period_err').on('click', '#old_period', function(){
        console.log(exist_period[2]);
    })
}


function set_selected_values(){
}





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







