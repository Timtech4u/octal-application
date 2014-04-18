/*global define*/
define(["backbone", "lib/kmapjs/collections/edge-collection", "octal/models/detailed-edge-model"], function(Backbone, EdgeCollection, DetailedEdgeModel){
  return  EdgeCollection.extend({
    model: DetailedEdgeModel
  });
});
