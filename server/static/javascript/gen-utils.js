// Create simple event liseners and utility functions for headers -- this may eventually be tied in with an MVC framework but it's pretty simple and universal at the moment
// requires: jQuery

/*global define*/
if (typeof window.define === "undefined"){
  var genutil = genFun($);
  genutil.prep();
}
else{
  define(["jquery", "sidr"], function($){
    return genFun($);
  } );
}


function genFun($){
  "use strict";
  return {
    prep: function(){
      $("#main").on("mousedown", function(evt){
          $.sidr('close', 'sidr-main');
      });
      $("#main").on("touchstart", function(evt){
        $.sidr('close', 'sidr-main');
      });

      /* sidr menu */
    $('#responsive-menu-button').sidr({
      name: 'sidr-main',
      source: '#header',
      side: "right"
    });

    }
  };
}
