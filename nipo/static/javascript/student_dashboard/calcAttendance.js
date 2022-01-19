// This file is simply broken. Needs to be entirely redone
// Student functionality in this project is miserable!
function getAttendance(){
	
	const url = '/module/attendance'

	//POST body data
	const user = {
		studentID: user_details.student_id,
		modulecode: course_select.value
	};

	//fetch request options
	const options = {
		method: 'POST',
		body: JSON.stringify(user),
		headers: {
			'Content-Type':'application/json'
		}
	}

	console.log(options);
	fetch(url,options)
		.then(res => res.json())
		.then(res => drawPie(res));

}

function drawBar(att_data){


	present_pc = att_data.Present_pc;
	absent_pc = att_data.Absent_pc;

	var present = {
	x: [present_pc],
	y: [att_data.module_name],
	name: 'Present',
	orientation: 'h',
	marker: {
	color: 'rgba(96,240,90,0.6)',
	width: 1
	},
	type: 'bar'
	};

	var absent = {
	x: [absent_pc],
	y: [att_data.module_name],
	name: 'Absent',
	orientation: 'h',
	type: 'bar',
	marker: {
	// color: 'rgba(255,153,51,0.6)',
	color: 'rgba(255,96,90,0.6)',
	width: 1
	}
	};

	var data = [present, absent];

	var layout = {
	//title: att_data.module_name + ' attendance summary',
	barmode: 'stack',
	height: 250,
	width: 600	
	};

	var config = {
		staticPlot:true,
		responsive:true,
		displaylogo: false
	}

Plotly.newPlot('attSum', data, layout, config);

}

function drawPie(att_data){

	present_pc = att_data.Present_pc;
	absent_pc = att_data.Absent_pc;

	var data = [{
	  values: [present_pc,absent_pc],
	  labels: ['Present', 'Absent'],
	  type: 'pie'
	}];

	var layout = {
	  width: '85%',
	  height: '80%' //Height doesnt matter. Aspect ratio to be set using width
	};


	Plotly.newPlot('attSum', data, layout);

}

// Add Plotly lib to HTML
pltly = document.createElement('script');
pltly.setAttribute('src','https://cdn.plot.ly/plotly-latest.min.js');
document.head.appendChild(pltly);


let pie_chart_canvas = document.getElementById('attSum');
let course_select = document.getElementById('courseList');
let body = document.body;

// var user_details;
// fetch('/userdetails')
// .then((resp) => resp.json())
// .then(function(data){ user_details = data});

var user_details;
	fetch('/userdetails')
	.then((resp) => resp.json())
	.then(function(data){ user_details = data})
	.then(course_select.addEventListener("change", getAttendance));
//body.addEventListener("load", getAttendance);
