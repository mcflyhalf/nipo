//alert(1);

//console.log(document.all)

//studinfo = document.querySelectorAll("span.stud-info")
fetch('/userdetails')
.then((resp) => resp.json())
.then(function(data){ console.log(data)});