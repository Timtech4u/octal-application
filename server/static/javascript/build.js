({
  baseUrl: ".",
  name: "main.js",
  out: "main-built.js",
    paths: {
    jquery:"//code.jquery.com/jquery-2.1.0.min",
    underscore: "lib/underscore",
    backbone: "lib/backbone-min",
    d3: "lib/d3",
    "btouch": "lib/backbone.touch",
  },
  shim: {
    d3: {
      exports: "d3"
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
