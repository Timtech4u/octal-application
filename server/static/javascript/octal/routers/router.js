define(["backbone", "jquery", "octal/models/quiz-model", "octal/views/quiz-view", "octal/views/edit-view", "lib/kmapjs/models/graph-model", "lib/kmapjs/views/graph-view"], function(Backbone, $, QuestionModel, QuizView, EditView, GraphModel, GraphView) {
    var pvt = { qviewId: "quiz-wrapper" };
	
	return router = Backbone.Router.extend({
        initialize: function() {},
        gid: null,
        routes: {
            "maps/:gid/concepts/:concept": "showQuiz",
            "maps/:gid/edit": "showEdit",
            "maps/:gid*path": "showIntro",
            "maps/new": "showEdit",
            "*path": "showError"
        },

        showEdit: function(gid) {
            var thisRoute = this;
            thisRoute.graphModel = new GraphModel();
            thisRoute.editView = new EditView({model: thisRoute.graphModel, appRouter: thisRoute});
            thisRoute.editView.render();
            $("#edit-view-wrapper").html(thisRoute.editView.$el).show();
            // oh god the hack
            window.editor_json = function() { return thisRoute.graphModel.toJSON(); };
        },

        showError: function() {
            $('#quiz-view-wrapper').html("<p>Sorry!  We don't recognize the URL you have entered!</p>");
        },

        showIntro: function(gid) {
            this.gid = gid;
            this.qview = new QuizView({gid: gid});
            this.qview.render();
            $("#quiz-view-wrapper").html(this.qview.$el).show();
            this.renderGraph();
        },

        showQuiz: function(gid, concept) {
            this.gid = gid;
            console.log("you have selected the concept: " + concept);


            var questionModel = new QuestionModel({concept: concept.toLowerCase(), gid: gid})
            var that = this;
            questionModel.fetch({
                success: function(model, response, options) {
                    that.qview = new QuizView({model: model});
                    that.qview.render();
                    $("#quiz-view-wrapper").html(that.qview.$el).show();
                },
                error: function(model, response, options) {
                    that.qview = new QuizView({gid: this.gid});
                    that.qview.render();
                    $("#quiz-view-wrapper").html(that.qview.$el).show();
                }
            });

            this.renderGraph();
        },
       renderGraph: function() {
            var thisRoute = this;

            //Initialize the graph model and view if they have not been initialized yet
            if(!thisRoute.graphModel) {
                thisRoute.graphModel = new GraphModel();
            }

            if(!thisRoute.graphView) {
                thisRoute.graphView = new GraphView({model: thisRoute.graphModel, appRouter: thisRoute, includeShortestOutlink: true });
                thisRoute.graphModel.addJsonNodesToGraph(oGlobals.auxData);

                thisRoute.graphView.optimizeGraphPlacement(false, false);
                thisRoute.graphView.render();
            }

            $("#graph-view-wrapper").html(thisRoute.graphView.$el).show();

        },
        changeUrlParams: function(paramsObj) {
            this.navigate("/maps/"+this.gid+"/concepts/" + paramsObj.focus, true);
        }

            /**$.ajax({url: "/maps/"+this.gid+"/exercises/fetch/" + concept + "/", async:false}).done(function(data) {
                model = new QuestionModel(data);
                model.set("concept",concept.toLowerCase());

             });**/

    });



});
