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
	modal_forms = parent_modal.getElementsByTagName("form");
	//TODO: Choose the form that isn't hidden
	if (modal_forms[0].classList.contains("hidden")) {
		modal_form = modal_forms[1];
	} else {
		modal_form = modal_forms[0];
	}
	modal_form.submit();
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

function show_form(formid) {
	form = document.getElementById(formid);
	form.classList.remove("hidden");
}

function hide_form(formid) {
	form = document.getElementById(formid);
	form.classList.add("hidden");
}

function show_form_hide_other(form_to_show_id, form_to_hide_id) {
	hide_form(form_to_hide_id);
	show_form(form_to_show_id);
}

function activate_tab_deactivate_other(tab_to_activate, tab_to_deactivate) {
	tab_to_activate.classList.add("is-active");
	tab_to_deactivate.classList.remove("is-active");
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

	// Activate the tabs to togle form and file upload sections
	tab_buttons = modal.getElementsByClassName("add-entity-tab");

	file_upload_tab = modal.getElementsByClassName("file-upload-tab");
	form_upload_tab = modal.getElementsByClassName("form-fill-tab");
	file_upload_tab = file_upload_tab[0];
	form_upload_tab = form_upload_tab[0];
	file_upload_activator = file_upload_tab.parentElement;
	form_upload_activator = form_upload_tab.parentElement;

	file_upload_form_id = tablename + "-file-upload"
	form_upload_form_id = tablename + "-record-upload"

	show_file_upload = show_form_hide_other.bind(null, file_upload_form_id, form_upload_form_id);
	show_form_upload = show_form_hide_other.bind(null, form_upload_form_id, file_upload_form_id);
	activate_file_upload = activate_tab_deactivate_other.bind(null, file_upload_activator, form_upload_activator);
	activate_form_upload = activate_tab_deactivate_other.bind(null, form_upload_activator, file_upload_activator);

	file_upload_tab.addEventListener("click", show_file_upload);
	file_upload_tab.addEventListener("click", activate_file_upload);
	form_upload_tab.addEventListener("click", show_form_upload);
	form_upload_tab.addEventListener("click", activate_form_upload);
}

