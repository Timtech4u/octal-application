from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from models import Graphs, Concepts, GraphForm
from utils import graphCheck, GraphIntegrityError, generateSecret
from apps.research.utils import getParticipantByUID, handleSurveys, urlLanding

import json

def display_all(request):
    graphs = Graphs.objects.filter(public=True).all()

    return render(request, "maps-all.html", {"maps":graphs})

def display(request, gid):
    try:
        graph = Graphs.objects.get(pk=gid)
    except Graphs.DoesNotExist:
        return HttpResponse(status=404)

    #OCTAL experiment: graph linearity based on user id
    p = None
    linear = 1
    pid = -1

    if graph.study_active:
        if request.user.is_authenticated():
            p = getParticipantByUID(request.user.pk, gid)

        #user has no participant ID yet, ask them for it
        if p is None:
            return HttpResponseRedirect(urlLanding(gid))

        # make sure participant completed the presurvey
        r = handleSurveys(p, gid)
        if r is not None: return HttpResponseRedirect(r)

        linear = int(p.linear)
        pid = int(p.pid)

    return render(request, "map.html",{"full_graph_skeleton":graph, 
                              "graph_name":graph.name,
                              "user_display":linear,
                              "pid": pid,
                              "study_active": int(graph.study_active),})

def new_graph(request):
    if request.method == 'POST':
        # form submission
        form = GraphForm(request.POST)
        if form.is_valid():
            # form is valid, save the graph
            graph = form.save()

            # build the concepts from the json
            graph.build(form.cleaned_data["graph_json"])

            return HttpResponseRedirect(reverse("maps:display", kwargs={"gid":graph.pk}))
    else:
        form = GraphForm(initial={'secret':generateSecret()})

    return render(request, "maps-new.html", {'form':form})

def edit(request, gid=""):
    return HttpResponse("editing a graph")

