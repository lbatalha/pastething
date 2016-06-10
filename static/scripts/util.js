document.addEventListener("DOMContentLoaded", function(event) { 
	"use strict";
	document.getElementById("wrap").addEventListener("click", wrap);
	document.getElementById("dir").addEventListener("click", dir);
	document.getElementById("indent").addEventListener("click", indent);
});
function wrap(evt){
    var lines = document.getElementsByClassName("pastelines");
    for(i in lines){
        lines[i].style.whiteSpace = 
            ((window.getComputedStyle(lines[i]).getPropertyValue("white-space") == "pre") ?
            "pre-wrap" :
            "pre";
    }
    evt.preventDefault
}
function dir(evt) {
	var dir = document.getElementById("wrapper");
    dir.setAttribute(
        "dir",
        dir.getAttribute("dir").split('').reverse().join('')
    );
	evt.preventDefault();
}
function indent(evt) {
	var lines = document.getElementsByClassName("pastelines");
	for(i in lines){
        lines[i].style.tabSize = "2";
		lines[i].style.tabSize =
            (window.getComputedStyle(lines[i]).getPropertyValue("tab-size") == "2") ?
            "4" :
            "8";
	}
	evt.preventDefault();
}

