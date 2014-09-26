//store selected time periods
//var current_periods = []; 

//store newspapers selection status
//{loc: all/none/other}
var newspaper_selection_status = {};

var default_dateStart = new Date(1913, 12, 1)
var default_dateEnd = new Date(1940, 11, 31)

$(document).ready(function(){

//============ Show/Hide analyses ================
$('#btn_show_analyses').click(function(){
    $(this).text(
        $(this).text().trim()=='Show analyses \u00bb'?'Hide analyses \u00AB':'Show analyses \u00bb'
    );
});



//=========== Query operations ==================
// Operations related to submit and specify
// search request. 
//================================================

//If the form is changed, set search result to start from 1
$('#advanced_search_form').change(function(){
    $('#page').val('1');
});

$('#advanced_search_form').keydown(function(){
    if (event.keyCode == 13){
        $('#page').val('1');
        $(this).submit();  
    }
});

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

//Advanced search: Datepicker
//Datepicker: Create selected pickers onloading
var periods = [];
if ($('#periods').val() != '')
    var periods = $('#periods').val().split(' ');

for(var i = 0; i<periods.length; i++){
    var dates = periods[i].split(':')
    $('#datepickers').append(make_datepicker(i, dates[0], dates[1]));
}

//Datepicker: activate the datepickers
$('.div_datepicker').each(function(){
    var id = $(this).attr('id').split('_')[1];
    var from_date = parseDate($('#datepicker_from_'+id).val());
    var to_date = parseDate($('#datepicker_to_'+id).val());
    if (from_date == '') from_date = default_DateStart;
    if (to_date == '') to_date = default_DateEnd;
    activate_datepicker(id, from_date, to_date);
})

//Datepicker: remove a datepicker
$('.rm-date').click(function(){
    $('#datepicker_'+$(this).attr('id').split('_')[1]).remove();
    set_input_dates(); 
});

//Datepicker: add a datepicker
$('#add_datepicker').click(function(){
    var current_ids = [];
    $('.div_datepicker').each(function(){
        current_ids.push(parseInt($(this).attr('id').split('_')[1]))
    })
    var id = 0;
    if (current_ids.length>0)
        id = Math.max.apply(Math, current_ids)+1;
    $('#datepickers').append(make_datepicker(id, '', ''));
    
    activate_datepicker(id, default_dateStart, default_dateEnd);
});


//Advancedsearch: clear the form
$('#btn_clearform').click(function(){
    $('.advanced_query_form').val('');

    //Clear the selected periods
    $('#datepickers').html('');
    set_input_dates(); 

    //And clear the newspaper selection
    $('select').selectpicker('deselectAll');
    $('select').selectpicker('val', []);
    set_newspaper_selections();
});

//Advanced search: set selected newspapers on loading
$('select').each(function(){
    var typenews = $(this).attr('id').split('_')[1];
    var selected = selected_newspapers[typenews];
    $(this).selectpicker('deselectAll');
    $(this).selectpicker('val', selected); 
});    
set_newspaper_selections();

//Advanced search: select all/none newspapers
$('select').on('change', function(){
    var typenews = $(this).attr('id').split('_')[1];
    var selection_status = newspaper_selection_status[typenews];
    var selected = $('option:selected', this);
    var selected = $(this).find(':selected');
    //only new selection needs to be handeled 
    //deselection are fine    
    var new_selection = ''
    selected.each(function(){
        var select_id = $(this).attr('id');
        if (selection_status[select_id] == false){
            new_selection = $('#'+select_id).text();
        }    
    });
    if (new_selection == 'All'){
        $(this).selectpicker('deselectAll');
        $(this).selectpicker('val', 'All');
    }
    else if (new_selection == 'None'){
        $(this).selectpicker('deselectAll');
        $(this).selectpicker('val', 'None');
    }
    else {
        if (selection_status['all_'+typenews] || selection_status['none_'+typenews]){
            $(this).selectpicker('deselectAll');
            $(this).selectpicker('val', new_selection); 
        }
    }
    //set the new selection
    set_newspaper_selections();
    
});


//=========================
// Pagination operations
//=========================
$('#li_right_pager').on('click', function(){
    var current_page = parseInt($('#page').val());
    //set the input value to new current_page
    $('#page').val(current_page + 1);
    //submit the form
    get_search_results();
});

$('#li_left_pager').on('click', function(){
    var current_page = parseInt($('#page').val());
    //set the input value to new current_page
    $('#page').val(current_page - 1);
    //submit the form
    get_search_results();
});

$('.li_pager').on('click', function(){
    $('#page').val($(this).attr('id').split('_')[2]);
    //submit the form
    get_search_results();
   
});

//===============================
// Sorting operations
//===============================
$('.opt_sort').click(function(){
    //set hidden input data
    $('.input_sort').val($(this).attr('data'));
    //set dropdown data
    $('#sortby').text($(this).text());
    //submit search
    if (current_qry_mode == 'simple')
        $('#simple_search_form').submit();
    else if (current_qry_mode == 'advanced')
        $('#advanced_search_form').submit();
});

//==============================
//Click on filtering
//===============================


});

//========== Functions =================


// ======= Query operations ===============
//  Functions related to query operations
// ========================================

//========= Datepicker functions ===================
function make_datepicker(idx, start, end){
    var id = 'datepicker_'+idx;
    var picker = [ 
        '<div class="input-group input-group-sm div_datepicker" id="'+id+'">',
        '<input type="text" class="form-control datepicker datepicker-from" ', 
        'value="'+start+'" ',
        'id="datepicker_from_'+idx+'">',
        '<span class="input-group-addon">to</span>',
        '<input type="text" class="form-control datepicker datepicker-to" ',
        'value="'+end+'" ',
        'id="datepicker_to_'+idx+'">',
        '<span class="input-group-addon glyphicon glyphicon-remove rm-date" id="rm_'+idx+'">',
        '</div>'
    ];
    return picker.join('\n');
}

function set_input_dates(){
    var dates = [];
    $('.div_datepicker').each(function(){
        var id = $(this).attr('id').split('_')[1];
        var from = $('.datepicker-from', this).val();
        var to = $('.datepicker-to', this).val();
        var to_add = true;
        if (from == '' && to == '')
            to_add = false;
        else if (from == '')
            from = '1914-01-01'
        else if (to == '')
            to = '1940-12-31' 
        if (to_add)
            dates.push(from + ':' + to);
    })
    $('#periods').val(dates.join(' '))
}

function activate_datepicker(id, from_date, to_date){
    $('#datepicker_from_'+id).datetimepicker({
        format: 'yyyy-mm-dd',
        startDate: default_dateStart,
        endDate: default_dateEnd,
        startView: 4,
        minView: 2,
        initialDate: from_date,
    })
    .on('changeDate', function(ev){
            var date = new Date(ev.date.valueOf());
            var date_string = date.getFullYear() 
                    + '-' + padStr(date.getMonth()+1) 
                    + '-' + padStr(date.getDate());

            $('#datepicker_to_'+id).datetimepicker('setStartDate', date_string);
            set_input_dates();
    }); 

    $('#datepicker_to_'+id).datetimepicker({
        format: 'yyyy-mm-dd',
        startDate: default_dateStart,
        endDate: default_dateEnd,
        startView: 4,
        minView: 2,
        initialDate: to_date,
    }).on('changeDate', function(ev){
            var date = new Date(ev.date.valueOf());
            var date_string = date.getFullYear() 
                    + '-' + padStr(date.getMonth()+1) 
                    + '-' + padStr(date.getDate());

            $('#datepicker_from_'+id).datetimepicker('setEndDate', date_string);
            set_input_dates();
    }); 
}

function parseDate(date_string){
    var date = date_string.split('-');
    return new Date(parseInt(date[0]), parseInt(date[1]), parseInt(date[2]));
}

function padStr(i) {
    return (i < 10) ? "0" + i : "" + i;
}


//=========Newspaper functions ===============
function set_newspaper_selections(){
  $('select').each(function(){
    var typenews = $(this).attr('id').split('_')[1];
    var options =  $(this).find('option');
    var sta = {}
    options.each(function(){
        sta[$(this).attr('id')] = $(this).is(':selected');
    });
    newspaper_selection_status[typenews] = sta;
  });
}


//========= Pagination functions ==========
// Functions related to paginations 
//=========================================

function get_search_results(){
    if (current_qry_mode == 'simple')
        $('#simple_search_form').submit();
    else if (current_qry_mode == 'advanced'){
        //console.log($('#advanced_search_form').attr('method'))
        $('#advanced_search_form').submit();
    }
}


//========= Visualization functions ============
// Functions related to visualizations
// Note: the actual drawing functions are in 
// vis.js
//==============================================




//================ OLD =================

/*
//Advanced_search: add time period
$('#btn_add_period').click(function(){
    //Get the filled in years
    var str_start = $('#period_start').val();
    var str_end = $('#period_end').val();
    if (str_start == '')
        start = 0;
    else
        start = parseInt(str_start);
    if (str_end == '')
        end = 0;
    else
        end = parseInt(str_end);
 
    if (check_year(start, end)){
        // Try to add the new period
        add_period(start, end);          
    }
});

//Advanced search: set the selected periods on loding

//$('#div_selected_periods').ready(function(){
var selected_periods = $('#input_selected_periods').val();
    if (selected_periods != ''){
    periods = selected_periods.split(';')
    for (var i = 0; i < periods.length; i++){
        var period = periods[i].split('-');
        current_periods.push([parseInt(period[0]), parseInt(period[1]), 'period_'+i]);
    }
    show_selected_periods();
}
//});
*/



/*
//Check the input time period
function check_year(syear, eyear) {
    err1 = 'Error: Input should be a 4-digit number between 1914 and 1940, inclusive.'
    err2 = 'Error: The starting year should not be later than the ending year.'

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

function show_selected_periods(){
    var added = []
    for (var i = 0; i<current_periods.length; i++){
        if (current_periods[i] == 0)
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
    var period_id = $(this).attr('id').replace('remove_', '');
    remove_selected_period(period_id);
    }); //End binding 
}

function remove_selected_period(period_id){
    $('#' + period_id).remove();
    // Set the element in the array empty  
    var idx = period_id.replace('period_', '');
        current_periods[idx] = 0;
    // Also reset the hidden input
    set_selected_values()
}

function add_period(start, end){
    //check its relation to existing periods
    var exists = current_periods.filter(function(d){
        return d[0] == start && d[1] == end;
    });
    //If already exists, do nothing
    if (exists.length == 0){
        //Check if it's covered by an existing period
        var relation = '';
        var conflict_period = [];
        // Check overlap
        var overlap = current_periods.filter(function(d){
            var dist = d[1]-d[0]
            return d != 0 && 
                (d[0] >= start-dist && d[0] <= end)||
                    (d[1] >= end && d[1] <= end+dist)
        }); 
        if (overlap.length > 0){
            relation = 'overlap';
            conflict_period = overlap;
            // If overlapped, further check covering
            // Check if it's covered by an existing period
            var covered = current_periods.filter(function(d){
                return d != 0 && d[0] <= start && d[1] >= end;
            });
            if (covered.length > 0) {
                relation = 'covered';
                conflict_period = covered;
            }
            else {
                //Check if it covers an existing period
                var cover = current_periods.filter(function(d){
                    return  d != 0 && d[0] >= start && d[1] <= end; 
                });
                if (cover.length > 0) {
                    relation = 'cover';
                    conflict_period = cover;
                }
            }
        }
                    
        //No overlap with existing periods 
        if (relation == ''){
            //Add the period to existing periods
            var id = current_periods.length;
            current_periods.push([start, end, 'period_'+id]);
            //Show selected period
            show_selected_periods();

            //Set the hidden input values
            set_selected_values();
        }
        else {
            warn_coverage([start, end], conflict_period, relation);
        }
    }
 
}

function warn_coverage(new_period, exist_periods, type){
    //Show warning a new period covers or is covered
    // by an existing period
    var content = ['<div class="alert alert-warning" role="alert">'];
    if (type == 'covered')
        content.push('The input period is covered by existing period(s).');
    else if (type == 'cover')
        content.push('The input period covers existing period(s). ');
    else if (type == 'overlap')
        content.push('The input period overlaps with existing period(s).');
    content.push('Please select the period you want to keep:<br/>');

    //Add selection buttons
    //New period
    content.push(
        '<button type="button" class="btn btn-default select_period" id="new_period">'
        + new_period[0] + '-' + new_period[1] + '</button>');
    //Existing periods
    for (var i = 0; i < exist_periods.length; i++){
        content.push([
            '<button type="button" class="btn btn-warning select_period old_period"', 
            'id="old_period_'+exist_periods[i][2]+'">',
            exist_periods[i][0] + '-' + exist_periods[i][1],
            '</button>'].join(' '));
    }
    //Merged overlaping period
    if (type == 'overlap'){
        var starts = []
        var ends = []
        exist_periods.forEach(function(d){
            starts.push(d[0]);
            ends.push(d[1]);
        })
        var min_start = Math.min(new_period[0], Math.min.apply(Math, starts));
        var max_end = Math.max(new_period[1], Math.max.apply(Math, ends));
        content.push(
            '<button type="button" class="btn btn-info select_period" id="merged_period">'
            + min_start + '-' + max_end + '</button>');
    }
    content.push('</div>');

    //Show an alert for warning
    $('#period_err').html(content.join(' '));
    //Bind listener to the button in the error msg 
    $('#period_err').on('click', '#new_period', function(){
        // Remove existing periods
        for (var j = 0; j<exist_periods.length; j++){
            remove_selected_period(exist_periods[j][2]);
        }
        // Dismiss warning
        $('#period_err').html('');
        // Try to add new period
        add_period(new_period[0], new_period[1])
    });
    $('#period_err').on('click', '.old_period', function(){
        // do nothing, dismiss warning
        $('#period_err').html('');
    })
    $('#period_err').on('click', '#merged_period', function(){
        var merged_period = $(this).text().split('-');
        // Remove conflicting periods
        for (var j = 0; j<exist_periods.length; j++){
            remove_selected_period(exist_periods[j][2]);
        }
        // Dismiss warning
        $('#period_err').html('');
        // Try to add this new period
        add_period(merged_period[0], merged_period[1]);
    });
}

//Set the selected time priod in the hidden input
function set_selected_values(){
    var values = [];
    for (var i = 0; i < current_periods.length; i++){
        if (current_periods[i] == 0)
            continue
        values.push(current_periods[i][0]+'-'+current_periods[i][1]);
    }
    $('#input_selected_periods').val(values.join(';'));  
}
*/


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
/*
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
*/

/*
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

function getRandomColor() {
    var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

*/





