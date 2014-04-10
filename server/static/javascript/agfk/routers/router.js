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

                var questionModel = this.getQuestionModel(concept);
                try {
                    thisRoute.qview = new QuizView({model: questionModel});
                    thisRoute.qview.render();
                } catch(e) {
                    console.log(e);
                }

                //Initialize the graph model and view if they have not been initialized yet
                if(!thisRoute.graphModel) {
                    thisRoute.graphModel = new GraphModel();
                }
                if(!thisRoute.graphView) {
                thisRoute.graphView = new GraphView({model: thisRoute.graphModel, appRouter: thisRoute, includeShortestOutlink: true });
                thisRoute.graphModel.addJsonNodesToGraph(agfkGlobals.auxData);

                thisRoute.graphView.optimizeGraphPlacement(false, false);
                thisRoute.graphView.render();
                }

                $("#quiz-view-wrapper").html(thisRoute.qview.$el).show();
                $("#graph-view-wrapper").html(thisRoute.graphView.$el).show();

        },
        changeUrlParams: function(paramsObj) {
            this.navigate("/concepts/" + paramsObj.focus, true);
        },
        getQuestionModel: function(concept) {
            $.ajax({url: "/octal/exercise/" + concept + "/", async:false}).done(function(data) {
            model = new QuestionModel(data);
            model.set("concept",concept.toLowerCase());
            });
        }

    });



});
