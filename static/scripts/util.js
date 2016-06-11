document.addEventListener("DOMContentLoaded", function(event) { 
	"use strict";
	document.getElementById("wrap").addEventListener("click", wrap);
	document.getElementById("dir").addEventListener("click", dir);
	document.getElementById("indent").addEventListener("click", indent);
});
function wrap(evt) {
	evt.preventDefault();
	var lines = document.getElementsByClassName("pastelines");
	var value = window.getComputedStyle(lines[0]).getPropertyValue("white-space")
	for(var i = 0, il = lines.length; i < il; i++){
		if(value == "pre"){
			lines[i].style.whiteSpace = "pre-wrap";
		}else{
			lines[i].style.whiteSpace = "pre";
		}
	}
}
function dir(evt) {
	evt.preventDefault();
	var dir = document.getElementById("wrapper");
	if(dir.getAttribute("dir") == "ltr"){
		dir.setAttribute("dir", "rtl");
	}else{
		dir.setAttribute("dir", "ltr");
	}		

}
function indent(evt) {
	evt.preventDefault();
	var lines = document.getElementsByClassName("pastelines");
	var value = window.getComputedStyle(lines[0]).getPropertyValue("tab-size")
	for(var i = 0, il = lines.length; i < il; i++){
		if(value == "2"){
			lines[i].style.tabSize = "4";
		}else if(value == "4"){
			lines[i].style.tabSize = "8";
		}else{
			lines[i].style.tabSize = "2";
		}
		
	}
	
}
