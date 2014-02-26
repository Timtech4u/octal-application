
/*global define*/
define(["backbone", "underscore", "lib/kmapjs/views/concept-list-item"], function (Backbone, _, ConceptListItem) {
  var pvt = {};

  pvt.consts = {
    templateId: "node-title-view-template", // name of view template (warning: hardcoded in html)
    implicitLearnedClass: "implicit-learned-concept-title",
    learnedCheckClass: "lcheck",
    learnedClass: "learned-concept-title",
    starredClass: "starred-concept-title"
  };
  pvt.consts = _.extend(ConceptListItem.prototype.getConstsClone(), pvt.consts);

  // return the list item view object
  return ConceptListItem.extend({
    events: {
        "click": function(evt){
          var thisView = this,
              modelId = thisView.model.id;

          if (!thisView.$el.hasClass(pvt.consts.clickedItmClass)) {
            // set focus if not currently focused
            thisView.model.trigger("setFocusNode", modelId);
          } else {
            // else, if currently focused, toggle scope
            thisView.model.trigger("toggleNodeScope", modelId);
          }
          // change url parameters if using a router
          this.appRouter && this.appRouter.changeUrlParams({focus: this.model.id});
        }
    },

    template: _.template(document.getElementById( pvt.consts.templateId).innerHTML),

    className: function(){
      var consts = pvt.consts,
          thisView = this,
          thisModel = thisView.model,
          aux = window.agfkGlobals.auxModel,
          id = thisModel.id;
      return pvt.consts.viewClass
        + (aux.conceptIsStarred(id) ? " " + consts.starredClass : "")
        + (aux.conceptIsLearned(id) ? " " + consts.learnedClass : "")
        + (thisModel.getImplicitLearnStatus() ? " " + consts.implicitLearnedClass : "");
    },

    events: function(){
      var levts = {
        "click .learn-view-check": function(evt){
          evt.stopPropagation();
          this.toggleConceptState(evt, "learn");
        },
        "click .learn-view-star": function(evt){
          evt.stopPropagation();
          this.toggleConceptState(evt, "star");
        }
      };
      return _.extend(ConceptListItem.prototype.events, levts);
    },

    /**
     * @override
     */
    postinitialize: function (inp) {
      var thisView = this,
          consts = pvt.consts,
          learnedClass = consts.learnedClass,
          implicitLearnedClass = consts.implicitLearnedClass,
          starredClass = consts.starredClass,
          nodeTag = thisView.model.id,
          aux = window.agfkGlobals.auxModel,
          gConsts = aux.getConsts();
      // set the app router
      thisView.appRouter = inp.appRouter;

      thisView.listenTo(aux, gConsts.learnedTrigger + nodeTag, function(nodeId, nodeSid, status){
        thisView.changeTitleClass(learnedClass, status);
      });
      thisView.listenTo(aux, gConsts.starredTrigger + nodeTag, function(nodeId, nodeSid, status){
        thisView.changeTitleClass(starredClass, status);
      });
      thisView.listenTo(thisView.model, "change:implicitLearnStatus", function(nodeId, nodeSid, status){
        thisView.changeTitleClass(implicitLearnedClass, status);
      });
    },

    /**
     * @override
     */
    postrender: function () {
      var thisView = this,
          thisModel = thisView.model;

      var h = _.clone(thisModel.toJSON());
      h.title = thisModel.getLearnViewTitle();
      thisView.$el.html(thisView.template(h));
    },

    /**
     * Toggle speficied state of given concept
     */
    toggleConceptState: function(evt, state){
      evt.stopPropagation();
      var aux = window.agfkGlobals.auxModel,
          nodeTag = this.model.id;
      state === "learn" ? aux.toggleLearnedStatus(nodeTag) : aux.toggleStarredStatus(nodeTag);
    }


  });
});
