//alert(1);

//console.log(document.all)

//studinfo = document.querySelectorAll("span.stud-info")
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
		.then(res => drawBar(res));

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
	  height: 200,
	  width: 250
	};


	Plotly.newPlot('attSum', data, layout);

}
pltly = document.createElement('script');
pltly.setAttribute('src','https://cdn.plot.ly/plotly-latest.min.js');
document.head.appendChild(pltly);


let pie_chart_canvas = document.getElementById('attSum')
let course_select = document.getElementById('courseList')

var user_details;
fetch('/userdetails')
.then((resp) => resp.json())
.then(function(data){ user_details = data});

// console.log(user_details)

course_select.addEventListener("change", getAttendance)

//---------------HTML---------------
// <head>
// 	<!-- Load plotly.js into the DOM -->
// 	<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>
// </head>

// <body>
// 	<div id='pieChart'><!-- Plotly chart will be drawn inside this DIV --></div>
// </body>



// //----------------JS---------------------------

//--------HTML-------
// <head>
// 	<!-- Load plotly.js into the DOM -->
// 	<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>
// </head>

// <body>
// 	<div id='attSum'><!-- Plotly chart will be drawn inside this DIV --></div>
// </body>




//---------JS-----------
// var present = {
//   x: [70, 90, 85],
//   y: ['mod1', 'mod2', 'mod3'],
//   name: 'Present',
//   orientation: 'h',
//   marker: {
//     color: 'rgba(55,128,191,0.6)',
//     width: 1
//   },
//   type: 'bar'
// };

// var absent = {
//   x: [30, 10, 15],
//   y: ['mod1', 'mod2', 'mod3'],
//   name: 'Absent',
//   orientation: 'h',
//   type: 'bar',
//   marker: {
//     color: 'rgba(255,153,51,0.6)',
//     width: 1
//   }
// };

// var data = [present, absent];

// var layout = {
//   title: 'All Module attendance summary',
//   barmode: 'stack'
// };

// Plotly.newPlot('attSum', data, layout);

// var data = [{
//   values: [85,15],
//   labels: ['Present', 'Absent'],
//   type: 'pie'
// }];

// var layout = {
//   height: 400,
//   width: 500
// };

// Plotly.newPlot('myDiv', data, layout);