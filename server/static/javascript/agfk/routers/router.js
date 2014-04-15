define(["backbone", "jquery", "agfk/models/quiz-model", "agfk/views/quiz-view", "lib/kmapjs/models/graph-model", "lib/kmapjs/views/graph-view"], function(Backbone, $, QuestionModel, QuizView, GraphModel, GraphView) {
    var pvt = { qviewId: "quiz-wrapper" };
	
	return router = Backbone.Router.extend({
        initialize: function() {},
        gid: null,
        routes: {
            "maps/:gid/concepts/:concept": "showQuiz",
            "maps/:gid*path": "showIntro",
            "*path": "showError"
        },

        showError: function() {
            $('#quiz-view-wrapper').html("<p>Sorry!  We don't recognize the URL you have entered!</p>");
        },


        showIntro: function(gid) {
            this.gid = gid;
            $("#quiz-view-wrapper").html("<p>Welcome to <strong>OCTAL</strong>, the Online Course Tool for Adaptive Learning.</p> <p>You will see a number of concepts and you can click on one to see an exercise associated with that concept. As you answer problems, this tool will try to predict your learning and it will highlight concepts with a <strong>green color</strong> that it estimates you understand well. This estimation of your understanding is a new feature so you should continue answering problems in any concept, green or not, if you like.</p> <p>Enjoy the tool, we hope you find it useful.</p>");
            this.renderGraph();
        },

        showQuiz: function(gid, concept) {
            this.gid = gid;
            qviewId = pvt.qViewId;
            console.log("you have selected the concept: " + concept);

            this.getQuestionModel(concept);

            thisRoute.renderGraph();
        },
        renderGraph: function() {
            var thisRoute = this;

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

            $("#graph-view-wrapper").html(thisRoute.graphView.$el).show();

        },
        changeUrlParams: function(paramsObj) {
            this.navigate("/maps/"+this.gid+"/concepts/" + paramsObj.focus, true);
        },
        getQuestionModel: function(concept) {
            $.ajax({url: "/maps/"+this.gid+"/exercises/fetch/" + concept + "/", async:false}).done(function(data) {
                model = new QuestionModel(data);
                model.set("concept",concept.toLowerCase());
                this.qview = new QuizView({model: model, baseurl: "/maps/"+this.gid});
                this.qview.render();
                $("#quiz-view-wrapper").html(this.qview.$el).show();
             });
        }

    });



});
