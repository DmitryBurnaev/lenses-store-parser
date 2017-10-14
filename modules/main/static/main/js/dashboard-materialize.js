/*================================================================================
	Item Name: Materialize - Material Design Admin Template
	Version: 3.1
	Author: GeeksLabs
	Author URL: http://www.themeforest.net/user/geekslabs
================================================================================

NOTE:
------
PLACE HERE YOUR OWN JS CODES AND IF NEEDED.
WE WILL RELEASE FUTURE UPDATES SO IN ORDER TO NOT OVERWRITE YOUR CUSTOM SCRIPT IT'S BETTER LIKE THIS. */


$(document).ready(function(){
    $(".sidebar-collapse").sideNav({edge: "left"});
    $('.modal').modal({
      	dismissible: true, // Modal can be dismissed by clicking outside of the modal
      	opacity: .5 // Opacity of modal background
    });
    $('select').material_select();
});