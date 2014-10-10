//store selected time periods
//var current_periods = []; 

//Define a delay function
var delay = (function(){
  var timer = 0;
  return function(callback, ms){
    clearTimeout (timer);
    timer = setTimeout(callback, ms);
  };
})();

var keyup_delay = 500;
var timeline_start = 1914;
var timeline_end = 1940

//store newspapers selection status
//{loc: all/none/other}
var newspaper_selection_status = {};

var default_dateStart = new Date(1913, 12, 1)
var default_dateEnd = new Date(1940, 11, 31)


$(document).ready(function(){

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

//remove loaded dates
$('.rm-date').on('click', function(){
    $('#datepicker_'+$(this).attr('id').split('_')[1]).remove();
    set_input_dates(); 
});

//Datepicker: activate the datepickers
$('.div_datepicker').each(function(){
    var id = $(this).attr('id').split('_')[1];
    var from_date = parseDate($('#datepicker_from_'+id).val());
    var to_date = parseDate($('#datepicker_to_'+id).val());
    if (from_date == '') from_date = default_DateStart;
    if (to_date == '') to_date = default_DateEnd;
    activate_datepicker(id, from_date, to_date);
})


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

    //remove a datepicker
    $('.rm-date').on('click', function(){
        $('#datepicker_'+$(this).attr('id').split('_')[1]).remove();
        set_input_dates(); 
    });

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


//============ Analyses ================

//When query terms are changed,change termclouds 
$('.query_term').keyup(function(){
    //update term cloud
    delay(function(){
        query = get_query()
        update_term_clouds(query);
    }, keyup_delay);
});

//When newspaper selection changed, change termclouds

//When query is submitted, create termclouds onload

//When click on a year, zoom in to the month view of the year


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
function update_term_clouds(query){
    if (query['must'].trim() == '' 
        && query['should'].trim() == '' 
        && query['mustnot'].trim() == '')
        return 0;

    //prepare wrap div
    var wraps = [];
    $('.np_group').each(function(){
        var loc_id = $(this).attr('id').split('_')[1]
        var loc = $(this).text();
        var label = '<h3>'+ loc +'</h3>';
        var wrap_div = ['<div class="termcloud_wrap" id="tc_'+loc_id+'">'];
        for (var year = timeline_start; year <= timeline_end; year++){
            //make the slot for each year
            var year_div = '<div>'+year+'</div>';
            var term_div = '<div id="cloud_terms_'+loc_id+'_'+year+'"></div>';
            var tc_div = ['<div class="termcloud" id="cloud_'+loc_id+'_'+year+'">',
                    year_div,
                    term_div,
                    '</div>'];
            wrap_div.push(tc_div.join(''));
        }
        wrap_div.push('</div>');
        wraps.push(wrap_div.join(''));
    });
    $('#analyses_termclouds').html(wraps.join('\n'));    
    
    //update year based termclouds
    for (var year = timeline_start; year <= timeline_end; year++){
        query['periods'] = year+'-01-01:'+year+'-12-31';
        query['year'] = year
        //console.log(query)
        $.ajax({
       	    type: "POST",
            url: url_vis_termclouds,
            data: query,

        }).done(function(response) {
            show_termcloud(response)    
        });
    }
}

function show_termcloud(data){
    console.log(year)
    var tc = data['tc']
    var papers = data['papers']
    var year = data['year'] 
    $.each(tc, function(key, value){
        var div_id = 'cloud_terms_'+key+'_'+year;
        var max_score = value[0][1];
        var min_score = value[value.length-1][1];
        var cloud = [];

        for (var i = 0; i<value.length; i++){
            var perc = (value[i][1]-min_score)/(max_score-min_score);
            var fontsize = Math.max(12+Math.round(10*perc)); 
            var opacity = 0.7+(0.3*perc);
            var concept = value[i][2]
            //console.log(value[i][0])
            //console.log(fontsize)
            var term = '<div class="tc-term" style="font-size: '+fontsize+'px; opacity: '+opacity+'">';
            term  = term + concept+'</div>';
            cloud.push(term);
        }
        $('#'+div_id).html(cloud.join(''));
       
    })  
}

//Collect current query for constructing term clouds
function get_query(){
    query = {};
    query['must'] = $('#must').val();
    query['should'] = $('#should').val();
    query['mustnot'] = $('#mustnot').val();

    newspapers = []
    $.each(newspaper_selection_status, function(key, value){
        news_select = []
        //if all is selected
        if (value['all_'+key])
            news_select = 'all';
        else if (value['none_'+key])
            news_select = 'none';
        else {
            selection = $.grep(Object.keys(value), function(k){
                return value[k] == true
            });
            news_select = selection.join(';');
        }
        query['newspapers_'+key] = news_select
     });
    return query
}


