// If you are looking at this file because you tried to mark 
// a student present or absent and it didnt work, 
// it is most probably because the session date chosen has 
// no class sessions.
// This will be fixed when only existing dates of the selected
// class session are returned in the HTML i.e. this is a backend
// matter with an existing issue that will be fixed eventually
// Let's hope we then remember to remove this comment


function getCurrentSessionDate(){
	let session_date = document.querySelectorAll(".small-container-a select");
	session_date = session_date[0].selectedOptions;
	session_date = session_date[0].value; 
	return session_date;

}

function markStudent(stud_id, status){
	
	const url = '/module/attendance/mark'

	let module_code = document.querySelectorAll(".small-container-b select");
	module_code = module_code[0].selectedOptions;
	module_code = module_code[0].value;
	let session_date = getCurrentSessionDate()

	//POST body data
	const attendance = {
		studentID: stud_id,
		modulecode: module_code,
		status: status,
		SessionDate: session_date
	};

	//POST request options
	const options = {
		method: 'POST',
		body: JSON.stringify(attendance),
		headers: {
			'Content-Type':'application/json'
		}
	};

	//TODO: Implement error detection here (Non-existent date, module, studID etc Would be done server side)
	fetch(url,options)
		.then(res => res.json())
		.then(res => setAttendanceAppearance(res, stud_id));

}

function setAttendanceAppearance(attData, stud_id){
	// This function receives the current appearance of the tile and sets the appropriate css class. 
	// Note that it doesnt actually change the status in the db. That is done by markPresent and markAbsent

	let attendance_data = attData.attendance;
	let session_date = getCurrentSessionDate();
	// TODO: Rework this dangerous string manipulation. 
	// Should be done in python
	session_date = session_date.replace("T", " ");
	session_date += ":00"
	
	// session_date = attData.attendance[session_date];
	let attendance_status = attData.attendance[session_date];
	if (attendance_status == 1){
		attendance_status = true;
	}
	else if (attendance_status == 0){
		attendance_status = false;
	}

	tile = document.getElementById(stud_id);

	if(attendance_status == true){
		tile.className = tile.className.replace("student-absent", "student-present")
	}
	else if(attendance_status == false){
		tile.className = tile.className.replace("student-present", "student-absent")
	}

}

// When page loads, get every student's tile-card element on the page by id (associate student id with tile-card)
let tile_wrapper = document.getElementsByClassName("tiles");
let student_tile = tile_wrapper[0].children;	//All individual student tiles
var student;

for (student of student_tile){
	let present_button = student.getElementsByClassName("present-btn");
	let absent_button = student.getElementsByClassName("absent-btn");
	let student_id = student.id;
	
	present_button[0].addEventListener("click",function() {markStudent(student_id, "Present");});
	absent_button[0].addEventListener("click",function() {markStudent(student_id, "Absent");});
}
