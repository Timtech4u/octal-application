/*
	This file contains the model for questions, retrieved from the server
*/

define(["backbone", "underscore"], function(Backbone) {

		var QuestionModel = Backbone.Model.extend({
				url: function() {
                    if(this.get("qid") != "-1") {
                        return this.instanceUrl + this.get("qid");
                    }
                    else {
                        return this.instanceUrl;
                    }
                },
				defaults: function() {
						return {
								qid: "-1", //question id
								h: "<p>Given the function definition:</p> <p style='text-align:center'><strong><em>f(N) = f(N -1) + f(N - 2)</em></strong></p><p>and an implementation not making use of memoization, what is the most likely asymptotic runtime as a function of N?</p>", //html of the question
								t: "0", //type of the question
								a: ["O(2^N)","O(N)","O(1)","O(N^2)"], //array including correct answer and perhaps distractors
								aid: "1",
                                cr:"0",
                                ct:"1"
						}
				},
				initialize: function(options) {
                    this.instanceUrl = "/maps/" + options.gid + "/exercises/fetch/" + options.concept + "/";
                    this.id = options.concept;
                    //this.on('change:a', function(){
                    //});
                },
                getBaseUrl: function() {
                    return "/maps/" + this.get("gid");
                }

				
		});
		return QuestionModel;
});
			 
