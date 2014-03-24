import json
import pdb

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from os import system

from apps.participant.utils import getParticipantByUID, handleSurveys

from forms import ContactForm

def get_full_graph_json_str():
    return '[{id:"algorithmic_complexity",title:"Algorithmic Complexity",deps:["lists","tail_recursion","tree_recursion"]},{id:"concurrency",title:"Concurrency",deps:["functions"]},{id:"conditionals",title:"Conditionals",deps:["variables"]},{id:"fractals",title:"Fractals",deps:["tree_recursion","tail_recursion"]},{id:"functions",title:"Functions",deps:["variables"]},{id:"lists",title:"Lists",deps:["loops"]},{id:"loops",title:"Loops",deps:["variable_mutation","conditionals"]},{id:"midterm",title:"Midterm",deps:["algorithmic_complexity","fractals","concurrency"]},{id:"tail_recursion",title:"Tail Recursion",deps:["functions"]},{id:"tree_recursion",title:"Tree Recursion",deps:["functions"]},{id:"variable_mutation",title:"Variable Mutation",deps:["variables"]},{id:"variables",title:"Variables",deps:[]}]'

def OctalView(request):
    concept_tag = request.path.split("/")[-1].split("#")[0]

    #OCTAL experiment: graph linearity based on user id
    p = None
    if request.user.is_authenticated():
        p = getParticipantByUID(request.user.pk)

    #user has no participant ID yet, ask them for it
    if p is None:
        return HttpResponseRedirect('/participant/')

    # make sure participant completed the presurvey
    r = handleSurveys(p)
    if r is not None: return r

    return render_to_response("app.html",{
                              "full_graph_skeleton": get_full_graph_json_str(), 
                              "user_display": int(p.linear),
                              "pid": int(p.pid),
                              }, context_instance=RequestContext(request))

