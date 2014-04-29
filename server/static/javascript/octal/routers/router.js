define(["backbone", "jquery", "octal/models/quiz-model", "octal/views/quiz-view", "octal/views/edit-view", "lib/kmapjs/models/graph-model", "lib/kmapjs/views/graph-view"], function(Backbone, $, QuestionModel, QuizView, EditView, GraphModel, GraphView) {
    var pvt = { qviewId: "quiz-wrapper" };
	
	return router = Backbone.Router.extend({
        initialize: function() {},
        gid: null,
        routes: {
            "maps/:gid/concepts/:concept": "showQuiz",
            "maps/:gid/edit": "showEdit",
            "maps/new": "showEdit",
            "maps/:gid*path": "showIntro",
            "*path": "showError"
        },

        showEdit: function(gid) {
            var thisRoute = this;

            // pull json from form
            var jstr = $('#id_graph-json_data').val();
            var json = (jstr) ? $.parseJSON(jstr) : null;

            // instantiate graph model with available json data
            thisRoute.graphModel = new GraphModel();
            if (json) thisRoute.graphModel.addJsonNodesToGraph(json);

            thisRoute.editView = new EditView({model: thisRoute.graphModel, appRouter: thisRoute});
            thisRoute.editView.optimizeGraphPlacement(false, false);
            thisRoute.editView.render();
            $("#edit-view-wrapper").html(thisRoute.editView.$el).show();

            // prevent zoom buttons from submitting form
            $('#edit-wrap button').click(function(e){ e.preventDefault(); });

            // oh god the hack
            window.editor_json = function() { 
                // build json out of the nodes in the model
                var concepts = [];
                thisRoute.graphModel.getNodes().forEach(function(con) {
                    window.tmpCon = con;
                    var tmpCon = { 
                        'id':con.id,
                        'title':con.attributes.title,
                        'dependencies':[]
                    };
                    con.get("dependencies").forEach(function(dep) {
                        tmpCon.dependencies.push({'source':dep.get("source").get("id")});
                    });
                    concepts.push(tmpCon);
                });
                if (concepts.length == 0) return "";
                return JSON.stringify(concepts);
            };
        },

        showError: function() {
            $('#quiz-view-wrapper').html("<p>Sorry! We don't recognize the URL you have entered!</p>");
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

            var questionModel = new QuestionModel({concept: concept.toLowerCase(), gid: gid})
            var that = this;
            questionModel.fetch({
                success: function(model, response, options) {
                    that.qview = new QuizView({model: model});
                    that.qview.render();
                    $("#quiz-view-wrapper").html(that.qview.$el).show();
                },
                error: function(model, response, options) {
                    that.qview = new QuizView({gid: that.gid});
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

                // hack alert: prevent kmap from showing edge wisps and summary toasts
                thisRoute.graphView.showEdgeSummary = function() {};
                thisRoute.graphView.showNodeSummary = function() {};
                thisRoute.graphView.isEdgeLengthBelowThresh = function() { return true; };

                thisRoute.graphView.optimizeGraphPlacement(false, false);
                thisRoute.graphView.render();
            }

            $("#graph-view-wrapper").html(thisRoute.graphView.$el).show();

        },
        changeUrlParams: function(paramsObj) {
            this.navigate("/maps/"+this.gid+"/concepts/" + paramsObj.focus, true);
        }

    });



});
