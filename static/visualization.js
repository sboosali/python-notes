// Util

function print(a,b,c,d,e,f,g){
  out = [];
  if (a) { out.push(a); }
  if (b) { out.push(b); }
  if (c) { out.push(c); }
  if (d) { out.push(d); }
  if (e) { out.push(e); }
  if (f) { out.push(f); }
  if (g) { out.push(g); }
  console.log(out.join(' '));
}

// the Graph

var svg = d3.select("svg")

function Width(){
	return parseFloat(svg.style('width'));
}
function Height(){
	return parseFloat(svg.style('height'));
}
var width = Width();
var height = Height();

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

//D3 flows

function font_size (d) {
    return d.fisheye.z * 30
}

function stroke_width (d) {
    var s = d.source.fisheye.z;
    var t = d.target.fisheye.z;
    var z = Math.max(s, t);
    return z * 10;
}

// DOM getters/setters

function Radius(){ return radius }

function Notes(notes) {
	// getter/setter
	// val() for <textarea> . text() for [contenteditable=true]
	if(typeof(notes)!=='undefined') {
		$('.notes').val(notes);
	}
	return $('.notes').val();
}
function Query(query) {
	// getter/setter
	// val() for <textarea>
  // text() for [contenteditable=true]
	if(typeof(query)!=='undefined') {
		$('.query').val(query);
	}
	return $('.query').val();
}

// Bound Box

function padding() {
	return 10;//Radius()/2;
}

function x(self, center) {
	var offset = self.getBoundingClientRect().width / 2;
	return bound_x(center, offset);
}

function y(self, center) {
	var offset = self.getBoundingClientRect().height / 2;
	return bound_y(center, offset);
}

function bound_x (x, dx) {
	x = Math.min(x, Width() - dx - padding());
	x = Math.max(x, 0 + dx + padding());
	return x;
}

function bound_y (y, dy) {
	y = Math.min(y, Height() - dy - padding());
	y = Math.max(y, 0 + dy + padding())
	return y;
}

// Hover/Click on Graph

var show = d3.select('.query').text();

var selected_start = 0;
var selected_end = 0;

function verbalize (d) {
	//return d.source.name + ' ' + d.name + ' ' + d.target.name;
  return d.show;
}

function enter_link (d) {
	Query(verbalize(d));
	select(d.lineno);
}

function leave_link() {
	Query(show);
	unselect();
}


function enter_node (d) {
	Query(d.name);
}

function leave_node() {
	Query(show);
}


function click_link (d) {
	show = verbalize(d);
	Query(show);
  query();

	select(d.lineno, true);
}

function click_node (d) {
	var elem = d3.select(this);

	show = d.name;
	Query(show);
  query();

	var transition = elem.transition().duration(100);

	d.fixed = true;
	elem.classed("fixed", true);
}

function fix (d,i){
	// elem[<... class=".fixed" .../>] ~> datum[d.fixed]
	if (d.fixed){
		var elem = d3.select(this);
		elem.classed("fixed", true);
	}
}

// Update Graph

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

// D3 loop

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

// Editing Notes

function visualize(graph) {

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

function draw() {
	var notes = Notes()
  if (!notes) {return;};

	var request = JSON.stringify({'notes': notes});
  print(request)

	d3.xhr("/draw").post(request, function (error, response) {
            if (error){
                alert('parsing error');
            }

            if (response){
	        		var graph = JSON.parse(response.responseText);
	        		visualize(graph);
            }
	})
}

// Select Text

function select(lineno, stay) {
		var elem = $('.notes').get(0);
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
	var elem = $('.notes').get(0);
  elem.focus();
  elem.selectionStart = selected_start;
  elem.selectionEnd = selected_end;
}

// Querying

function query(){
  var query = Query().trim();
  if (!query) {return;}

	var request = JSON.stringify({'query': query});
	print(request)

	d3.xhr("/query").post(request, function (error, response) {
            if (error){
                alert('querying error');
            }

            if (response){
	        		var data = JSON.parse(response.responseText);
							var results = data['results']
              results = results.join('\n')
              d3.select('.results').text(results)
            }
	})
}

d3.select('.query').on('focus', draw);
// forces redraw to make what you see consistent with the results

d3.select('.query').on('blur', query);

// Keyboard Shortcuts

var pressed = {};
var enterKey = 13;
var tabKey = 9;

$('.notes').on('keydown', function(e) {
   pressed[e.keyCode] = true;
   handleEdit(e);
});

$('.notes').on('keyup', function(e) {
   pressed[e.keyCode] = false;
});

function handleEdit(e) {
   if (pressed[enterKey] && e.shiftKey) {
      e.preventDefault();
      e.stopPropagation();
      draw();
   }
}

$('.query').on('keydown', function(e) {
   pressed[e.keyCode] = true;
   handleQuery(e);
});

$('.query').on('keyup', function(e) {
   pressed[e.keyCode] = false;
});

function handleQuery(e) {
   if (pressed[enterKey] && e.shiftKey) {
      e.preventDefault();
      e.stopPropagation();
      query();
   }
}

// Cyclic Tabbing

$('[tabindex=2]').on('keydown', function(e) {
  if (e.keyCode===tabKey) {
    e.preventDefault();
    e.stopPropagation();
    $('[tabindex=1]').focus();
  }
})

// Persistence

var Storage = {

  set: function(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
  },

  get: function(key) {
    var value = localStorage.getItem(key);
    return value && JSON.parse(value);
  }
}

function persist() {
  Storage.set('notes', Notes());
}

$(window).on('unload', persist)

function restore() {
  Notes(Storage.get('notes'));
  print('(restoring)', Storage.get('notes'));
}

$(restore);
