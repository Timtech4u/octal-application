
/*global define
This file contains general purpose utility functions
*/

define(["jquery"], function($){
  "use strict";

  var utils = {};

  /**
   * Check if input is a url
   */
  utils.isUrl = function(inStr) {
    var regexp = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
    return regexp.test(inStr);
  };

  /**
   * Controls window/svg/div sizes in two panel display when resizing the window
   * NB: has jQuery dependency for x-browser support
   */
  utils.scaleWindowSize = function(header_id, main_id) {
    var windowSize = {
      height: 0,
      mainHeight: 0,
      headerHeight: 0,
      setDimensions: function() {
        windowSize.height = $(window).height();
        windowSize.headerHeight = $('#' + header_id).height();
        windowSize.mainHeight = windowSize.height - windowSize.headerHeight;
        windowSize.updateSizes();
      },
      updateSizes: function() {
        $('#' + main_id).css('height', windowSize.mainHeight + 'px');
      },
      init: function() {
        if ($('#' + main_id).length) {
          windowSize.setDimensions();
          $(window).resize(function() {
            windowSize.setDimensions();
          });
        }
      }
    };
    windowSize.init();
  };

  // return require.js object
  return utils;
});
