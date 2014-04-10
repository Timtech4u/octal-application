define(["backbone", "jquery", "agfk/models/quiz-model", "agfk/views/quiz-view", "lib/kmapjs/models/graph-model", "lib/kmapjs/views/graph-view"], function(Backbone, $, QuestionModel, QuizView, GraphModel, GraphView) {
    var pvt = {
				qviewId: "quiz-wrapper"
		};

	
	return router = Backbone.Router.extend({
        initialize: function() {
				},
				
				routes: {
						"":"showError",
						"concepts/:concept": "showQuiz"
				},
				
				showError: function() {
					  console.log("you must specify a concept");
				},


				showQuiz: function(concept) {
                        var thisRoute = this,
						qviewId = pvt.qViewId;
						console.log("you have selected the concept: " + concept);
						var questionModel = new QuestionModel({concept: concept});
						thisRoute.qview = new QuizView({model: questionModel});
						thisRoute.qview.render();
                        thisRoute.graphModel = new GraphModel();
                        thisRoute.graphView = new GraphView({model: thisRoute.graphModel, appRouter: thisRoute, includeShortestOutlink: true });
                        thisRoute.graphModel.addJsonNodesToGraph(agfkGlobals.auxData);
                        thisRoute.graphView.render();
						$("#quiz-view-wrapper").html(thisRoute.qview.$el).show();
                        $("#graph-view-wrapper").html(thisRoute.graphView.$el).show();

				},
                changeUrlParams: function(paramsObj) {
                    this.navigate("/concepts/" + paramsObj.focus, true);
                }
		});

});
