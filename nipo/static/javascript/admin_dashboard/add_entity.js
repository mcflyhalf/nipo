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
		//File upload
		modal_form = modal_forms[1];
		// const headers = {
		// 'Content-Type': 'multipart/form-data'
		// }
	} else {
		//Single record upload
		modal_form = modal_forms[0];
		// const headers = {
		// 'Content-Type': 'application/x-www-form-urlencoded'
		// }
	}
	// modal_form.submit();
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

function show_form(formid) {
	form = document.getElementById(formid);
	form.classList.remove("hidden");
}

function hide_form(formid) {
	form = document.getElementById(formid);
	form.classList.add("hidden");
}

function show_form_hide_others(form_to_show_id, forms_to_hide_ids) {
	for (id of forms_to_hide_ids){ 
		hide_form(id);
	}
	show_form(form_to_show_id);
}

function activate_tab_deactivate_others(tab_to_activate, tabs_to_deactivate) {
	for (tab of tabs_to_deactivate){
		tab.classList.remove("is-active");		
	}
	tab_to_activate.classList.add("is-active");
}

// --------------------add_entity.main()-------------------
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
}

add_entity_modals = Array.from(modals)
  				   .filter(modal => modal.classList.contains("adder-modal"))

for (modal of add_entity_modals){

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

	show_file_upload = show_form_hide_others.bind(null, file_upload_form_id, [form_upload_form_id]);
	show_form_upload = show_form_hide_others.bind(null, form_upload_form_id, [file_upload_form_id]);
	activate_file_upload = activate_tab_deactivate_others.bind(null, file_upload_activator, [form_upload_activator]);
	activate_form_upload = activate_tab_deactivate_others.bind(null, form_upload_activator, [file_upload_activator]);

	file_upload_tab.addEventListener("click", show_file_upload);
	file_upload_tab.addEventListener("click", activate_file_upload);
	form_upload_tab.addEventListener("click", show_form_upload);
	form_upload_tab.addEventListener("click", activate_form_upload);
}



// ----------------attach_to_module.js code----------------------------------
function attachToModuleFormSubmit(){
	// submit the appropriate(visible) attach to module form
	atm_forms = document.getElementsByClassName("attach-to-module-form")
	form = 	Array.from(atm_forms)
  				 .filter(form => !form.classList.contains("hidden"))

  	form = form[0]

	if (form.id.includes("file-upload")){
		const headers = {
		'Content-Type': 'multipart/form-data'
		}
	} else {
		//Single record upload
		const headers = {
		'Content-Type': 'application/x-www-form-urlencoded'
		}
	}
	// form.submit();
	const formdata = new FormData(form);

	const options = {
		method: 'POST',
		body: formdata,
	};
	url = form.action;

	fetch(url,options)
		.then(res => res.json())
		.then(res => checkStatus.bind(null,res["request-id"]))
		.then(boundFunc => doLater(boundFunc, 5000));
}

// -----------------attach_to_module.main()-----------------------------

// Cause attachers to open the modal
let att_modal_id = "mod-attach-to-module"; //id of the attacher modal
let attachers = document.getElementsByClassName("attacher");
//Bind used to solve the problem discussed in
//https://stackoverflow.com/questions/19586137/addeventlistener-using-for-loop-and-passing-values
//Need to learn to add event listener with params. Bind seems clunky
showM = showModal.bind(null, att_modal_id);

// bind show modal event listener to all attacher buttons
for (attacher of attachers){
	attacher.addEventListener("click",showM);
}

attacher_modals = Array.from(modals)
  				   .filter(modal => modal.classList.contains("attacher-modal"))

for (modal of attacher_modals){
	

	let submit_btn = modal.getElementsByClassName("submit-form");

	for (btn of submit_btn){
		btn.addEventListener("click", attachToModuleFormSubmit);
	}

	tab_buttons = modal.getElementsByClassName("attach-to-module-tab");

	file_upload_tab = modal.getElementsByClassName("file-attach-tab");
	form_upload_tab = modal.getElementsByClassName("individual-attach-tab");
	entire_course_attach_tab = modal.getElementsByClassName("entire-course-attach-tab");
	file_upload_tab = file_upload_tab[0];
	form_upload_tab = form_upload_tab[0];
	entire_course_attach_tab = entire_course_attach_tab[0];
	file_upload_activator = file_upload_tab.parentElement;
	form_upload_activator = form_upload_tab.parentElement;
	entire_course_attach_activator = entire_course_attach_tab.parentElement;

	file_upload_form_id = "attach-to-module-file-upload-form"
	form_upload_form_id = "attach-to-module-individual-form"
	entire_course_attach_form_id = "attach-to-module-entire-course-form"

	show_file_upload = show_form_hide_others.bind(null, file_upload_form_id, [entire_course_attach_form_id,form_upload_form_id]);
	show_form_upload = show_form_hide_others.bind(null, form_upload_form_id, [entire_course_attach_form_id,file_upload_form_id]);
	show_entire_course_attach = show_form_hide_others.bind(null, entire_course_attach_form_id, [form_upload_form_id, file_upload_form_id]);
	activate_file_upload = activate_tab_deactivate_others.bind(null, file_upload_activator, [entire_course_attach_activator, form_upload_activator]);
	activate_form_upload = activate_tab_deactivate_others.bind(null, form_upload_activator, [entire_course_attach_activator, file_upload_activator]);
	activate_entire_course_attach = activate_tab_deactivate_others.bind(null, entire_course_attach_activator, [form_upload_activator, file_upload_activator]);

	file_upload_tab.addEventListener("click", show_file_upload);
	file_upload_tab.addEventListener("click", activate_file_upload);
	form_upload_tab.addEventListener("click", show_form_upload);
	form_upload_tab.addEventListener("click", activate_form_upload);
	entire_course_attach_tab.addEventListener("click", show_entire_course_attach);
	entire_course_attach_tab.addEventListener("click", activate_entire_course_attach);

}



