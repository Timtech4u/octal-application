({
  baseUrl: ".",
  name: "main.js",
  out: "main-built.js",
    paths: {
    jquery:"lib/jquery-1.10.2",
    underscore: "lib/underscore",
    backbone: "lib/backbone-min",
    d3: "lib/d3",
    "btouch": "lib/backbone.touch",
    "colorbox": "lib/jquery.colorbox-min",
    "completely": "lib/complete.ly.1.0.1"
  },
  shim: {
    completely: {
      exports: "completely"
    },
    d3: {
      exports: "d3"
    },
    colorbox: {
      deps: ["jquery"]
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
  }
})
