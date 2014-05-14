({
  baseUrl: ".",
  name: "main.js",
  out: "main-built.js",
    paths: {
    jquery:"//code.jquery.com/jquery-2.1.0.min",
    underscore: "//cdnjs.cloudflare.com/ajax/libs/underscore.js/1.6.0/underscore-min",
    backbone: "//cdnjs.cloudflare.com/ajax/libs/backbone.js/1.1.2/backbone-min",
    d3: "//cdnjs.cloudflare.com/ajax/libs/d3/3.4.5/d3.min",
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
