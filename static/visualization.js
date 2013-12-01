
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
    .charge(-400)
    .linkDistance(30)
    .size([width, height]);

//

var distortion = 100;
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

function verbalize (d) {
	return d.source.name + ' ' + d.name + ' ' + d.target.name;
}

function enter_link (d) {
	d3.select('.show').text(verbalize(d));
}

function enter_node (d) {
	d3.select('.show').text(d.name);
}

function leave_link() {
	d3.select('.show').text(show);
}

function leave_node() {
	d3.select('.show').text(show);
}

function click_link (d) {
	show = verbalize(d);
	d3.select('.show').text(show);

	var link = d3.select(this);
}

function click_node (d) {
	var node = d3.select(this);

	show = d.name;
	d3.select('.show').text(show);

	var transition = node.transition().duration(100);

	transition
		.attr('x', 0)
		.attr('y', 0)
		.attr('px', 0)
		.attr('py', 0)
		.attr('fisheye', {'x': 0, 'y': 0, 'z': 1});

	d.fixed = true;
  node.classed("fixed", true);
}

//

function visualize(error, response) {
	var graph = JSON.parse(response.responseText);

	force.nodes([]).links([]);

  force
      .nodes(graph.nodes)
      .links(graph.links)
      .start();

	var drag = force.drag();

  var link = svg.selectAll(".link")
      .data(graph.links)
    .enter().append("line")

  link
      .attr("class", "link")
      .style("stroke-width", function(d) { return 10; });

  var node = svg.selectAll(".node")
      .data(graph.nodes).enter().append("text");

  node
      .attr("class", "node")
      .attr('text-anchor', "middle")
      .call(drag);

  node.text(function(d) { return d.name; });

	node.on('mouseenter', enter_node);
	node.on('mouseleave', leave_node);
	node.on('click', click_node)

	link.on('mouseenter', enter_link);
	link.on('mouseleave', leave_link);
	link.on('click', click_link);

  //

	function tick() {
    node.each(function(d) { d.fisheye = fisheye(d); });

		node.attr("x", function (d) { return x(this, d.fisheye.x); })
        .attr("y", function (d) { return y(this, d.fisheye.y); })
        .attr('font-size', font_size);

    link.attr("x1", function(d) { return x(this, d.source.fisheye.x); })
        .attr("y1", function(d) { return y(this, d.source.fisheye.y); })
        .attr("x2", function(d) { return x(this, d.target.fisheye.x); })
        .attr("y2", function(d) { return y(this, d.target.fisheye.y); })
        .style('stroke-width', stroke_width);
  }

  svg.on("mousemove", function() {
		fisheye.focus(d3.mouse(this));
    tick();
  });

  force.on("tick", tick);

};

//

function Notes(notes) {
	// getter/setter
	if(typeof(notes)!=='undefined') {
		$('.notes').val(notes);
	}
	return $('.notes').val();
}

d3.xhr('example.note', function (error, response) {
	Notes(response.responseText);
	draw();
});

function draw() {
	var notes = {'notes': Notes()};
	d3.xhr("/draw").post(JSON.stringify(notes), visualize);
}

d3.select('.query').on('click', draw);

//
