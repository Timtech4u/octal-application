import json
import pdb

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from content_server import database
import config

from os import system

from apps.participant.utils import getParticipantByUID, handleSurveys

from forms import ContactForm

def get_full_graph_json_str():
    return '[{"id":"algorithmic_complexity","title":"Algorithmic Complexity","dependencies":[{"source":"lists"},{"source":"tail_recursion"},{"source":"tree_recursion"}]},{"id":"concurrency","title":"Concurrency","dependencies":[{"source":"functions"}]},{"id":"conditionals","title":"Conditionals","dependencies":[{"source":"variables"}]},{"id":"fractals","title":"Fractals","dependencies":[{"source":"tree_recursion"},{"source":"tail_recursion"}]},{"id":"functions","title":"Functions","dependencies":[{"source":"variables"}]},{"id":"lists","title":"Lists","dependencies":[{"source":"loops"}]},{"id":"loops","title":"Loops","dependencies":[{"source":"variable_mutation"},{"source":"conditionals"}]},{"id":"midterm","title":"Midterm","dependencies":[{"source":"algorithmic_complexity"},{"source":"fractals"},{"source":"concurrency"}]},{"id":"tail_recursion","title":"Tail Recursion","dependencies":[{"source":"functions"}]},{"id":"tree_recursion","title":"Tree Recursion","dependencies":[{"source":"functions"}]},{"id":"variable_mutation","title":"Variable Mutation","dependencies":[{"source":"variables"}]},{"id":"variables","title":"Variables","dependencies":[]}]'

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

