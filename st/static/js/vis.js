//draw a timeline plot

//id: the id of the element for the visualization
//data: {concept: [(date, count)...]}
//color_code: {concept: {date: count}}
function draw_timeline(id, data, color_code){
    var m = [20, 20, 20, 20];
    var w = $('#vis_area').width()-m[1] - m[3];
    var h = 300 - m[0] - m[2];
    
    var x, y;
    
    //the canvas
    var svg = d3.select(id).append('svg')
            .attr('width', w + m[1] + m[3])
            .attr('height', h + m[0] + m[2])
        .append('g')
            .attr('transform', 'translate(' + m[3] + ',' + m[0] + ')'); 

        
};


