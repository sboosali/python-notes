
var number_of_prints = 0;
function print(x, n){
	if(typeof(n)==='undefined') {
			console.log(x);
	}
  else if (number_of_prints < n) {
		number_of_prints++;
		console.log(x);
	}
}

//

var svg = d3.select("svg")

function Width(){
	return parseFloat(svg.style('width'));
}
function Height(){
	return parseFloat(svg.style('height'));
}
var width = Width();
var height = Height();

//

var force = d3.layout.force()
    .charge(-2000)
    .linkDistance(30)
		//.gravity(0) //TODO box bound
    .size([width, height]); //TODO

var drag = force.drag();

var distortion = 50;
var radius = 100;
var fisheye = d3.fisheye.circular()
    .distortion(distortion)
		.radius(radius);

//

function font_size (d) {
    return d.fisheye.z * 30
}

function stroke_width (d) {
    var s = d.source.fisheye.z;
    var t = d.target.fisheye.z;
    var z = Math.max(s, t);
    return z * 10;
}

//

function x(_, cx) { return cx;}
function y(_, cy) { return cy;}

// function x(self, center) {
// 	var offset = self.getBoundingClientRect().width / 2;
// 	return bound_x(center, offset);
// }

// function y(self, center) {
// 	var offset = self.getBoundingClientRect().height / 2;
// 	return bound_y(center, offset);
// }

// function bound_x (x, dx) {
// 	x = Math.min(x, Width() - dx - Radius()/2);
// 	x = Math.max(x, 0 + dx + Radius()/2);
// 	return x;
// }

// function bound_y (y, dy) {
// 	y = Math.min(y, Height() - dy - Radius()/2);
// 	y = Math.max(y, 0 + dy + Radius()/2)
// 	return y;
// }

//

var show = d3.select('.show').text();

var selected_start = 0;
var selected_end = 0;

function verbalize (d) {
	return d.source.name + ' ' + d.name + ' ' + d.target.name;
}


function enter_link (d) {
	d3.select('.show').text(verbalize(d));
	select(d.lineno);
}

function leave_link() {
	d3.select('.show').text(show);
	unselect();
}


function enter_node (d) {
	d3.select('.show').text(d.name);
}

function leave_node() {
	d3.select('.show').text(show);
}


function click_link (d) {
	show = verbalize(d);
	d3.select('.show').text(show);

	select(d.lineno, true);
}

function click_node (d) {
	var elem = d3.select(this);

	show = d.name;
	d3.select('.show').text(show);

	var transition = elem.transition().duration(100);

	// transition
	// 	.attr('x', 0)
	// 	.attr('y', 0)
	// 	.attr('px', 0)
	// 	.attr('py', 0)
	// 	.attr('fisheye', {'x': 0, 'y': 0, 'z': 1});

	d.fixed = true;
	elem.classed("fixed", true);
}

//

var names = {};
// stores old nodes
// index nodes:[_] by _.name

function merge(nodes) {
	// keep existing position/momentum/fixedness
	for (var i=0; i < nodes.length; i++) {

		var next = nodes[i];
		var prev = names[nodes[i].name]; // defaults to null
		var node = $.extend(true, {}, next, prev); // merge old into new
		nodes[i] = node;

		names[node.name] = node;
	}
	return nodes;
}

function node_id (d){
	return d.name;
}

function link_id (d){
	var id = d.source.name +'___'+ d.name +'___'+ d.target.name;
	return id;
}

//

function start(node, link) {
	link.enter().append("line");
  link.attr("class", "link")
      .style("stroke-width", function(d) { return 10; });
	link.exit().remove();

	node.enter().append("text");
  node.attr("class", "node")
      .attr('text-anchor', "middle")
      .call(drag);
	node.exit().remove();

  node.text(function(d) { return d.name; });

	node.on('mouseenter', enter_node);
	node.on('mouseleave', leave_node);
	node.on('click', click_node)

	link.on('mouseenter', enter_link);
	link.on('mouseleave', leave_link);
	link.on('click', click_link);

	force.start();
}

function fix (d,i){
	// elem[<... class=".fixed" .../>] ~> datum[d.fixed]
	if (d.fixed){
		var elem = d3.select(this);
		elem.classed("fixed", true);
	}
}

function tick(node, link) {
	node.each(function(d) { d.fisheye = fisheye(d); })
			.each(fix);

	node.attr("x", function (d) { return x(this, d.fisheye.x); })
			.attr("y", function (d) { return y(this, d.fisheye.y); })
			.attr('font-size', font_size);

  link.attr("x1", function(d) { return x(this, d.source.fisheye.x); })
			.attr("y1", function(d) { return y(this, d.source.fisheye.y); })
			.attr("x2", function(d) { return x(this, d.target.fisheye.x); })
			.attr("y2", function(d) { return y(this, d.target.fisheye.y); })
			.style('stroke-width', stroke_width);
}

//

function visualize(error, graph) {

	merge(graph.nodes);

	force.nodes(graph.nodes).links(graph.links).start();
	// force.start() initializes link.source and link.target
	// from an index into the node array, to an element inside the node array

	var node = svg.selectAll(".node").data(force.nodes(), node_id);
	var link = svg.selectAll(".link").data(force.links(), link_id);

	start(node, link);

	svg.on("mousemove", function() {
		fisheye.focus(d3.mouse(this));
    tick(node, link);
  });

	force.on("tick", function() { tick(node, link) });

};

//

function Notes(notes) {
	// getter/setter
	// val() for <textarea> . text() for [contenteditable=true]
	if(typeof(notes)!=='undefined') {
		$('.notes').val(notes);
	}
	return $('.notes').val();
}

function draw() {
	var notes = {'notes': Notes()};
	var request = JSON.stringify(notes);
	d3.xhr("/draw").post(request, function (error, response) {
		var graph = JSON.parse(response.responseText);
		visualize(error, graph);
	})
}

d3.select('.query').on('click', draw);

//

d3.xhr('notes/dad.note', function (error, response) {
  var text = response.responseText //.replace(/\n/g, '<br>')
	Notes(text);
	draw();

// 	var notes = $('#notes').get(0)
// 	var range = document.createRange();
//   range.selectNodeContents(notes)

// 	var selection = window.getSelection();
//   selection.removeAllRanges();
//   selection.addRange(range);

});

//

function select(lineno, stay) {
		var elem = $('#notes').get(0);
		var text = Notes();
    var lines = text.split("\n");

    // start/end
    var start = 0
		var end = text.length;
    for(var i = 0; i < lines.length; i++) {
        if(i == lineno) {
            break;
        }
        start += (lines[i].length+1);
    }
    var end = lines[lineno].length+start;

    // focus and select
		elem.focus();
    elem.selectionStart = start;
    elem.selectionEnd = end;

	  if (stay === true) {
			selected_start = start;
			selected_end = end;
		}
}

function unselect() {
	var elem = $('#notes').get(0);
  elem.focus();
  elem.selectionStart = selected_start;
  elem.selectionEnd = selected_end;
}

//TODO localstorage

var pressed = {};

$('body').on('keydown', function(e) {
   pressed[e.keyCode] = true;
   handleKey(e);
});

$('body').on('keyup', function(e) {
   pressed[e.keyCode] = false;
   handleKey(e);
});

var enter = 13;
function handleKey(e) {
   if (pressed[enter] && e.shiftKey) {
      draw();
   }
}

//

