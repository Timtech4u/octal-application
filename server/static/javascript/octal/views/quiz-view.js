define(["backbone", "underscore", "jquery", "octal/models/quiz-model"], function(Backbone, _, $, QuestionModel){

    var shuffle = function(array) {
        for(var j, x, i = array.length; i; j = Math.floor(Math.random() * i), x = array[--i], array[i] = array[j], array[j] = x);
        return array;
    }

    return (function() {
            var pvt = {};
            pvt.viewConsts = {
                templateId: "quiz-view-template",
                altTemplateId: "quiz-error-view-template",
                viewId: "quiz",
                knownColor: '#EDFFED',
                neutralColor: "#F6FBFF",
                unknownColor: "#FA3333"
            };
            pvt.isRendered = false;
            pvt.knownConcepts = [];
            pvt.graphRendered = false;
            pvt.newQuestion = true;
            pvt.correct = false;

            var ans = "";

            return Backbone.View.extend({

                initialize: function(options) { this.options = options; },

                template: _.template(document.getElementById( pvt.viewConsts.templateId).innerHTML),

                tagName:  'div',

                isViewRendered: function(){
                        return pvt.isRendered;
                },

                events: {
                        'click .submit-button': 'submit'
                },

                // Re-render the title of the todo item.
                render: function() {
                    //prevent scrolling
                    $("body").css("overflow", "hidden");

                    if(!this.model) {
                        this.template = _.template(document.getElementById(pvt.viewConsts.altTemplateId).innerHTML);
                        h = {
                            gid: this.options.gid, 
                            studyActive:oGlobals.studyActive,
                            participant:oGlobals.participant
                        };
                        this.$el.html(this.template(h));
                        this.getKnowledgeState("/maps/"+this.options.gid);
                        return;
                    }

                    //Get local variables
                    pvt.isRendered = false;
                    var thisView = this;
                    var thisModel = thisView.model;
                    pvt.correct = false;

                    //Get the current concept, compare it to the concept last served by the view
                    //If they don't match, we need to deal with the new question
                    thisView.concept = thisModel.get('concept');
                    if(pvt.conceptName != thisView.concept) {
                        pvt.newQuestion = true;
                    }

                    //Remove the underscores for rendering the concept
                    thisModel.set("title",thisModel.get("concept").replace(/_/g, " "));

                    //If we are serving a new question, update the correct answer we
                    //are looking for
                    if(pvt.newQuestion) {
                        ans = thisModel.get("a")[0];
                        pvt.newQuestion = false;
                    }

                    //Shuffle the order of the answer choices and render the view
                    thisModel.set("a", shuffle(thisModel.get("a")));
                    var h = _.clone(thisModel.toJSON());
                    h.participant = oGlobals.participant;
                    h.linear = oGlobals.linear;
                    h.studyActive = oGlobals.studyActive;
                    h.gid = thisView.model.get("gid");

                    thisView.$el.html(thisView.template(h));

                    //Add some behavior to the check-answer and next question buttons
                    //TODO: I wonder if there isn't a better way/place to do this
                    thisView.$el.find('#check-answer').click(function() {
                       thisView.submit();
                    });
                    thisView.$el.find('#next-question-button').click(function() {
                       thisView.getNextQuestion();
                    });
                    //If this is the last question in a concept, take away the next button
                    if(thisModel.get('cr') == 1) {
                        thisView.$el.find('#next-question-button').hide();
                    }

                    pvt.isRendered = true;

                    this.getKnowledgeState(thisModel.getBaseUrl());
                    return this;
                },

                reattachGraph: function() {
                    this.$el.find('#graph-wrapper').append(pvt.expView.el);
                },

                //Logic dictating attempt submission
                submit: function() {
                    var thisView = this;
                    var attempt = $("input[type='radio'][name='answer']:checked").val();

                    if(attempt && !pvt.correct) {
                        //Check client-side if the question answer is correct
                        pvt.correct = (ans==attempt) ? 1 : 0;
                        var correctness = pvt.correct;
                        var aid = thisView.model.get('aid');

                        //If the question is correct, indicate that this is the case
                        if(correctness) {
                            $('#question-feedback').fadeOut(100,function(){$(this).html('Correct!  Great job!').css('color','#46a546').fadeIn()});
                            $('#check-answer').hide();
                            $cc = $('#correct-count');
                            if((parseInt($cc.html()) + 1) == thisView.model.get('ct')) {
                                $('#next-question-button').show()
                            }
                            $cc.fadeOut(100,function(){$(this).html(parseInt($cc.html()) + 1).fadeIn()});
                            //Make the next question button available again if a user has finished all the questions in a category
                        }
                        else
                            $('#question-feedback').fadeOut(100,function(){$(this).html('Try again!').css('color','black').fadeIn()});

                        // csrf protection
                        // https://docs.djangoproject.com/en/dev/ref/contrib/csrf/
                        function csrfSafeMethod(method) {
                            // these HTTP methods do not require CSRF protection
                            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
                        }

                        $.ajaxSetup({
                            crossDomain: false, // obviates need for sameOrigin test
                            beforeSend: function(xhr, settings) {
                                if (!csrfSafeMethod(settings.type)) {
                                    xhr.setRequestHeader("X-CSRFToken", oGlobals.csrftoken);
                                }
                            }
                        });

                        //get new model from the server
                        //request to submit an answer

                        $.ajax({
                            url: thisView.model.getBaseUrl() + "/exercises/attempt/" + aid + "/" + correctness,
                            type: "PUT",
                            async: false,
                            dataType: "text",
                            success: function(data) {
                                //Don't allow resubmission if the question was correct
                                if(!correctness)
                                    thisView.model.set('aid',data);
                            }
                        })
                        //request to get new question
                        thisView.getKnowledgeState(thisView.model.getBaseUrl());
                    } else if(!attempt) {
                        $('#question-feedback').fadeOut(100,function(){$(this).html('Make sure to select a response!').css('color','black').fadeIn()});
                    }

                    //console.log(thisView.model.get("aid"));

                    //SOME LOGIC GOES HERE FOR HIGHLIGHTING NODES
                    //rerender the view TODO: seems kinda wasteful to totally rerender the view rather than the question

                },

                getNextQuestion: function() {
                    pvt.conceptName = this.model.get("concept");
                    var thisView = this;
                    thisView.model.fetch({
                        success: function(model, response, options) {
                            pvt.newQuestion = true;
                            pvt.correct = false;
                            thisView.model = model;
                            thisView.render();
                        }
                    });
                    /*)
                    $.ajax({
                        url: thisView.options.baseurl + "/exercises/fetch/" + pvt.conceptName + "/" + thisView.model.get('qid'),
                        async:false
                    }).done(function(data) {
                        thisView.model = new QuestionModel(data);
                        thisView.model.set("concept", pvt.conceptName);
                    });
                    pvt.newQuestion = true;
                    pvt.correct = false;
                    this.render();
                    */
                },


                getKnowledgeState: function(baseURL) {
                    thisView = this;

                    $.ajax({
                        url: baseURL+"/ki/"
                    }).done(function(data) {
                        pvt.knownConcepts = data;
                        thisView.highlightNodes();
                        //thisView.getKnowledgeState(data);
                    });

                },
                highlightNodes: function() {
                    if(!oGlobals.linear) {
                        //console.log(pvt.knownConcepts)
                        //mega-ghetto
                        $('circle').css('fill',pvt.viewConsts.neutralColor);
                        for (var i = 0; i < pvt.knownConcepts.length; i++) {
                            try {
                                $($('#circlgG-' + pvt.knownConcepts[i]).find('circle')[0]).css('fill', pvt.viewConsts.knownColor);
                            } catch (TypeError) {
                                //do nothing, node not in graph
                            }
                        }
                    } else {
                        $('.learn-title-display').css('background-color', pvt.viewConsts.neutralColor);
                        for (var i = 0; i < pvt.knownConcepts.length; i++) {
                            try {
                                $('#node-title-view-' + pvt.knownConcepts[i]).css('background-color', pvt.viewConsts.knownColor);
                            } catch (TypeError) {
                                //do nothing, node not in graph
                            }
                        }
                    }
                },
                edit: function() { },

                close: function() {
                        //$('#header').css('display', 'block');
                }

            });
    })();


    // log reference to a DOM element that corresponds to the view instance

});
