({
  baseUrl: ".",
  name: "main.js",
  out: "main-built.js",
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
  }
})
