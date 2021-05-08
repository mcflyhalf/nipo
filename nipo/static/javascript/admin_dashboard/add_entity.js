//hide all modals
function hideModals(){
	let modals = document.getElementsByClassName("modal");

	for (modal of modals){
		modal.classList.remove("is-active");
	}
}

//Ensures only specified modal is visible
function showModal(modalid){
	hideModals();
	let visibleModal = document.getElementById(modalid);
	visibleModal.classList.add("is-active");
	// return false;
}

function reportStatus (status){
	// console.log(status)

	if (status['status'] == "SUCCESS") {
		alert("successfully added entity");
	} else if (status['status'] == "FAILURE") {
		alert("failed to add entity");
	} else {
		alert("unknown status of entity")
	}
}

function checkStatus(task_id){
	let url = '/status/'+ task_id;

	fetch(url)
		.then(res => res.json())
		.then(stat => reportStatus(stat));
}

function doLater(boundFunc, delay){
	setTimeout(boundFunc, delay);
}

function addEntity(tablename){
	//Add a new entity to the table tablename in the db
	//Function still being built out e.g. name may need to change
	

	parent_modal = document.getElementById("mod-"+tablename);
	modal_form = parent_modal.getElementsByTagName("form");
	modal_form = modal_form[0];

	const formdata = new FormData(modal_form);

	const options = {
		method: 'POST',
		body: formdata,
	};
	url = modal_form.action;

	fetch(url,options)
		.then(res => res.json())
		.then(res => checkStatus.bind(null,res["request-id"]))
		.then(boundFunc => doLater(boundFunc, 5000));
}

hideModals();
// For each add-fooin the summary tiles, add an event listener
// to display the Modal foo
let adders = document.getElementsByClassName("adder");

for (adder of adders){
	//Adder id and modal id
	aid = adder.attributes["id"]["value"];
	mid = "mod"+aid.slice("add".length);	//Replace "add" from the beginning with "mod"
	
	//Bind used to solve the problem discussed in
	//https://stackoverflow.com/questions/19586137/addeventlistener-using-for-loop-and-passing-values
	let showM = showModal.bind(null, mid)

	adder.addEventListener("click",showM);
}


//For each modal, add necessary event listeners
let modals = document.getElementsByClassName("modal")

for(modal of modals){

	close_buttons = modal.getElementsByClassName("close-modal")
	for (button of close_buttons){
		button.addEventListener("click",hideModals);
	}

	let tablename=modal.getAttribute('id');
	tablename = tablename.slice("mod-".length);
	let addE = addEntity.bind(null, tablename);
	let submit_btn = modal.getElementsByClassName("submit-form");

	for (btn of submit_btn){
		btn.addEventListener("click", addE);
	}
}

