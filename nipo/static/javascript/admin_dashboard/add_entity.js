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

function getFormDetails(tablename){
	//Gets details of the form and validates
	//(so we dont have to send a post request)
	//and we can use js instead


	//Get the form's parent modal
	parent_modal = document.getElementById("mod-"+tablename);
	// console.log(parent_modal);
	modal_form = parent_modal.getElementsByTagName("form");
	modal_form = modal_form[0];
	inputs = modal_form.getElementsByTagName("input");
	let formDeets = {};
	formDeets['Has Empty Fields'] = false;
	form[tablename]= tablename;

	for (input of inputs){
		formDeets[input.name]=input.value;
		if(input.value == ''){
			formDeets['Has Empty Fields'] = true;
		}
	}

	console.log('getFormDetails has been called');
	// console.log(formDeets);


}

function addEntity(tablename){
	//Add a new entity to the table tablename in the db
	//Function still being built out e.g. name needs to change
	//Steps:
	// let formDeets= getFormDetails(tablename);
	// if (formDeets['Has Empty Fields']){
	// 	// TODO: Convert to a banner visible on page
	// 	console.log('Not sending anything, some fields are empty')
	// 	return
	// }

	parent_modal = document.getElementById("mod-"+tablename);
	modal_form = parent_modal.getElementsByTagName("form");
	modal_form = modal_form[0];
	modal_form.submit();

	const formdata = new FormData(modal_form);
	// const XHR = new XMLHttpRequest();
	// // Bind the FormData object and the form element
	// // Define what happens on successful data submission
	// XHR.addEventListener( "load", function(event) {
	//   console.log( event.target.responseText );
	//   console.log(event);
	// } );
	// // Define what happens in case of error
	// XHR.addEventListener( "error", function(event) {
	//   console.log( event.target.responseText );
	//   console.log(event);
	// } );

	// // Set up our request
	// XHR.open("POST", modal_form.action);

	// // The data sent is what the user provided in the form
	// XHR.send(formdata);

  

	const options = {
		method: 'POST',
		body: formdata,
	};
	url = modal_form.action;

	fetch(url,options)
		.then(res => res.json())
		.then(res => console.log(res));


	console.log(modal_form);




	//1. Send Post request to backend to add entity
		//Post request is json obj with:
			//*tablename
			//*All other form fields
		//What is marshalling and unmarshalling?
		//Backend will call a function on the tablename
		//And pass in a dict of the json params as values
		//Test that sqlinjection is not possible using this method
		//Clear form input fields


	//2. Receive response with task id



	//3. Poll 5 seconds later to check for task completion
	// (Requires task id)



	//4. Put banner on page confirming addition of entity


	//test for csrf
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

