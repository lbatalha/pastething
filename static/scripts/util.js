document.addEventListener("DOMContentLoaded", function(event) { 
	"use strict";
	document.getElementById("rm").addEventListener("click", token);
	document.getElementById("wrap").addEventListener("click", wrap);
	document.getElementById("dir").addEventListener("click", dir);
	document.getElementById("indent").addEventListener("click", indent);
});
function wrap(evt) {
	var lines = document.getElementsByClassName("pastelines");
	for(var i = 0, il = lines.length; i < il; i++){
		if(window.getComputedStyle(lines[i]).getPropertyValue("white-space") == "pre"){
			lines[i].style.whiteSpace = "pre-wrap";
		}else{
			lines[i].style.whiteSpace = "pre";
		}
		
	}
	evt.preventDefault();
}
function dir(evt) {
	var dir = document.getElementById("wrapper");
	if(dir.getAttribute("dir") == "ltr"){
		dir.setAttribute("dir", "rtl");
	}else{
		dir.setAttribute("dir", "ltr");
	}		
	evt.preventDefault();
}
function indent(evt) {
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
	evt.preventDefault();
}

function token(evt) {
	var value = document.getElementById("token");
	window.location.href = window.location.href + "/" + value;
}
