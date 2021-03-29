//hide all modals
function hideModals(){
	let modals = document.getElementsByClassName("modal");

	for (modal of modals){
		modal.classList.remove("is-active");
	}
}

//Ensures only specified table is visible
function showModal(modalid){
	hideTables();
	let visibleModal = document.getElementById(modalid);
	visibleModal.classList.add("is-active");
	// return false;
}

hideModals();
// For each add-something, add an event listener
// to display the Modal something
let adders = document.getElementsByClassName("adder");

for (adder of adders){
	//Adder id and modal id
	aid = adder.attributes["id"]["value"];
	mid = "mod"+aid.slice("add".length);	//Remove "view-"" from the beginning
	
	//Bind used to solve the problem discussed in
	//https://stackoverflow.com/questions/19586137/addeventlistener-using-for-loop-and-passing-values
	let showM = showModal.bind(null, mid)

	adder.addEventListener("click",showM);
}

let close_buttons = document.getElementsByClassName("close-modal");

for (button of close_buttons){
	button.addEventListener("click",hideModals);
}
