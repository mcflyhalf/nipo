//hide all tables
function hideTables(){
	let tables = document.getElementsByTagName("table");

	for (table of tables){
		table.style.display = "none";
	}
}

//Ensures only specified table is visible
function showTable(tableid){
	hideTables();
	let visibleTable = document.getElementById(tableid);
	visibleTable.style.display = "inline-table";
	return false;
}

hideTables();
//For each view-something, add an event listener
//to display the table something
let viewers = document.getElementsByClassName("viewer");

for (viewer of viewers){
	vid = viewer.attributes["id"]["value"];
	tid = vid.slice("view-".length);	//Remove "view-"" from the beginning
	
	//Bind used to solve the problem discussed in
	//https://stackoverflow.com/questions/19586137/addeventlistener-using-for-loop-and-passing-values
	let showT = showTable.bind(null, tid)

	viewer.addEventListener("click",showT);
}
