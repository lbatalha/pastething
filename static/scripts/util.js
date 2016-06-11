document.addEventListener("DOMContentLoaded", function(event) { 
	"use strict";
	document.getElementById("wrap").addEventListener("click", wrap);
	document.getElementById("dir").addEventListener("click", dir);
	document.getElementById("indent").addEventListener("click", indent);
});
function wrap(evt) {
	evt.preventDefault();
	var lines = document.getElementsByClassName("pastelines");
	for(var i = 0, il = lines.length; i < il; i++){
		if(window.getComputedStyle(lines[i]).getPropertyValue("white-space") == "pre"){
			lines[i].style.whiteSpace = "pre-wrap";
		}else{
			lines[i].style.whiteSpace = "pre";
		}
	}
}
function dir(evt) {
	evt.preventDefault();
	var dir = document.getElementById("wrapper");
	dir.setAttribute(
		"dir",
		dir.getAttribute("dir").split('').reverse().join('')
	);

}
function indent(evt) {
	evt.preventDefault();
	var lines = document.getElementsByClassName("pastelines");
	for(var i = 0, il = lines.length; i < il; i++){
		if(window.getComputedStyle(lines[i]).getPropertyValue("tab-size") == "2"){
			lines[i].style.tabSize = "4";
		}else if(window.getComputedStyle(lines[i]).getPropertyValue("tab-size") == "4"){
			lines[i].style.tabSize = "8";
		}else{
			lines[i].style.tabSize = "2";
		}
		
	}
	
}
