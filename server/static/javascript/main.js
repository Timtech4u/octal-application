/**
 * Main function, set to data-main with require.js
 */

/*global requirejs */

// configure require.js
requirejs.config({
  baseUrl: window.STATIC_PATH + "javascript",
  paths: {
    jquery: "lib/jquery-2.1.0.min",
    underscore: "lib/underscore-1.6.0-min",
    backbone: "lib/backbone-1.1.2-min",
    d3: "lib/d3-3.4.5.min",
    "dagre": "lib/dagre",
    "btouch": "lib/backbone.touch",
  },
  shim: {
    d3: {
      exports: "d3"
    },
    dagre: {
      exports: "dagre"
    },
    underscore: {
      exports: "_"
    },
    backbone: {
      deps: ['underscore', 'jquery'],
      exports: 'Backbone'
    },
    "btouch": {
      deps: ["jquery", "underscore", "backbone"]
    }
  },
  waitSeconds: 15
});

/**
 * Handle uncaught require js errors -- this function is a last resort
 * TODO: anyway to reduce code repetition with other js files, considering the other js files won't be loaded?
 * perhaps define a global namespace of css classes and ids?
 */
if (window.PRODUCTION){
  requirejs.onError = function(err){
    var errorId = "error-message";
    if (document.getElementById(errorId) === null){
      var div = document.createElement("div");
      div.id = errorId;
      div.className = "app-error-wrapper"; // must also change in error-view.js
      div.textContent = "Sorry, it looks like we encountered a problem trying to " +
        "initialize the application. Refreshing your browser may solve the problem.";
      document.body.appendChild(div);
    }
    throw new Error(err.message);
  };
}

// octal app
requirejs(["backbone", "utils/utils", "octal/routers/router", "jquery", "btouch"], function(Backbone, Utils, AppRouter, $){
  "use strict";

  // shim for CSRF token integration with backbone and django
  var oldSync = Backbone.sync;
  Backbone.sync = function(method, model, options){
    options.beforeSend = function(xhr){
      if (model.get("useCsrf")){
        xhr.setRequestHeader('X-CSRFToken', window.CSRF_TOKEN);
      }
    };
    return oldSync(method, model, options);
  };

  // automatically resize window when viewport changes
  Utils.scaleWindowSize("header", "main");

  // load any JS defined on the page
  if (typeof pageUtils === 'function') pageUtils();

  var appRouter = new AppRouter();
  Backbone.history.start({ pushState:true} );

});
