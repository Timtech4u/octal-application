
define(["backbone", "underscore", "jquery", "octal/utils/utils", "agfk/models/quiz-model"], function(Backbone, _, $, Utils, QuestionModel){

    var shuffle = function(array) {
            for(var j, x, i = array.length; i; j = Math.floor(Math.random() * i), x = array[--i], array[i] = array[j], array[j] = x);
            return array;
    }

    var QuizView = (function() {
            var pvt = {};
            pvt.viewConsts = {
                    templateId: "quiz-view-template",
                    viewId: "quiz",
                    knownColor: '#EDFFED',
                    neutralColor: "#F6FBFF",
                    unknownColor: "#FA3333"
            };
            pvt.isRendered = false;
            pvt.expView;
            pvt.paramsObj;
            pvt.graphRendered = false;

            pvt.conceptName = window.location.href.split('/').pop().split('#').shift();


            var ans = "";

            return Backbone.View.extend({

                    concept: pvt.conceptName,

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
                            pvt.isRendered = false;
                            var thisView = this;

                            var thisModel = thisView.model;

                            //var thiseView = thisView.options.appRouter.eview;

                            thisView.concept = thisModel.get('concept');
                            thisView.$el.empty();
                            thisModel.set("concept",thisModel.get("concept").replace(/_/g, " "));
                            ans = thisModel.get("a")[0];
                            thisModel.set("a", shuffle(thisModel.get("a")));
                            var h = _.clone(thisModel.toJSON());

                            thisView.$el.html(thisView.template(h));
                            if( !pvt.graphRendered) {
                                //add graph view as subview to quiz view.  view.
                                var expView = thisView.options.appRouter.expView;
                                pvt.expView = expView;
                                var fnode = thisView.options.appRouter.graphModel.getNode(thisView.concept);
                                thisView.options.appRouter.expView.centerForNode(fnode);
                                thisView.options.appRouter.expView.setFocusNode(fnode);
                                thisView.$el.find('#graph-wrapper').append(expView.el);
                                var svg = expView.el.getElementsByTagName('svg')[0];
                                //svg.setAttribute('viewBox', '0, -800, 1200, 1000');
                                //set border thicker on current node
                                //thisView.$el.find("#"+ pvt.conceptName).find('ellipse').css('stroke-width',7)
                                pvt.graphRendered = true;
                            } else {
                                thisView.$el.find('#graph-wrapper').append(pvt.expView.el);
                            }


                            pvt.isRendered = true;
                            this.highlightNodes();

                            return this;


                    },
                    reattachGraph: function() {
                        this.$el.find('#graph-wrapper').append(pvt.expView.el);
                    },

                    //If no button selected, returns undefined
                    submit: function() {
                            var thisView = this;
                          var attempt = $("input[type='radio'][name='answer']:checked").val();
                            console.log(ans);
                            var correctness = (ans==attempt) ? 1 : 0;
                            pvt.conceptName = window.location.href.split('/').pop().split('#').pop().split('&').shift().split('=').pop();
                            var sid = agfkGlobals.auxModel.get('nodes').get(pvt.conceptName).get('sid');
                            var aid = thisView.model.get('aid');
                            console.log(aid);

                            if(correctness)
                                    alert('correct');
                            else
                                    alert('incorrect');

                            //get new model from the server
                            //request to submit an answer

                            $.ajax({
                                    url: "/octal/attempt/" + aid + "/" + correctness,
                                    type: "PUT",
                                    async: false

                            })

                            //request to get new question

                            $.ajax({
                                    url: "/octal/exercise/" + sid,
                                    async:false
                            }).done(function(data) {
                                    if ( console && console.log ) {
                                            thisView.model = new QuestionModel(data);
                                            thisView.model.set("concept", pvt.conceptName);
                                    }
                            });

                            console.log(thisView.model.get("aid"));


                            //SOME LOGIC GOES HERE FOR HIGHLIGHTING NODES
                            //rerender the view TODO: seems kinda wasteful to totally rerender the view rather than the question
                            this.render();
                    },
                    highlightNodes: function() {
                            thisView = this;
                            var sid = agfkGlobals.auxModel.get('nodes').get(pvt.conceptName).get('sid');

                            $.ajax({
                                url: "/octal/knowledge/" + sid,

                            }).done(function(data) {
                                    //thisView.highlightNodes(data);
                                    console.log(data)
                                    //mega-ghetto
                                    thisView.$el.find('ellipse').css('fill',pvt.viewConsts.neutralColor);
                                    //for (var i = 0; i < unknownConcepts.length; i++) {
                                    //	this.$el.find("#"  + unknownConcepts[i]).find('ellipse').css('fill', pvt.viewConsts.unknownColor);
                                    //}
                                    for (var i = 0; i < data.length; i++) {
                                        try {
                                            $($('#circlgG-' + pvt.expView.model.getNode(data[i]).cid ).find('circle')[0]).css('fill', pvt.viewConsts.knownColor);
                                        } catch (TypeError) {
                                            //do nothing, node not in graph
                                        }
                                    }
                            });

                    },
                    edit: function() {

                    },

                    close: function() {
                            //$('#header').css('display', 'block');
                    }


            });
    })();


    // log reference to a DOM element that corresponds to the view instance

    return QuizView;
});
