import json
import pdb

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
import config

from os import system

from apps.participant.utils import getParticipantByUID, handleSurveys
from apps.octal.models import Graph

from forms import ContactForm

def OctalView(request):
    concept_tag = request.path.split("/")[-1].split("#")[0]

    graph = Graph.objects.get(pk=0)

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
                              "full_graph_skeleton": graph, 
                              "user_display": int(p.linear),
                              "pid": int(p.pid),
                              }, context_instance=RequestContext(request))

