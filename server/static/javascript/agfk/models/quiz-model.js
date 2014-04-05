/*
	This file contains the model for questions, retrieved from the server
*/

define(["backbone", "underscore"], function(Backbone) {

		var QuestionModel = Backbone.Model.extend({
				urlRoot:"../api/questions",
				defaults: function() {
						return {
								qid: "1", //question id
								h: "<p>Given the function definition:</p> <p style='text-align:center'><strong><em>f(N) = f(N -1) + f(N - 2)</em></strong></p><p>and an implementation not making use of memoization, what is the most likely asymptotic runtime as a function of N?</p>", //html of the question
								t: "0", //type of the question
								a: ["O(2^N)","O(N)","O(1)","O(N^2)"], //array including correct answer and perhaps distractors
								aid: "1",
                                cr:"0",
                                ct:"1"
						}
				},
				initialize: function() {
						this.on('change:a', function(){
								console.log('- the answer value for this model has been changed');
						});
				},
                getNextQuestion: function(conceptName) {

                         $.ajax({
                                url: "/octal/exercise/" + sid + "/" + thisView.model.get('qid'),
                                async:false
                            }).done(function(data) {
                                thisView.model = new QuestionModel(data);
                                thisView.model.set("concept", pvt.conceptName);
                            });
                            pvt.newQuestion = true;
                            pvt.correct = false;
                            this.render();
                    },
				
		});
		var QuestionCollection = Backbone.Collection.extend({
				model: QuestionModel,
                url:"../api/questions"
		});
		return QuestionModel;
});
			 
