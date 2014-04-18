from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.core.urlresolvers import reverse

from models import Graphs, Concepts, GraphForm
from utils import graphCheck, GraphIntegrityError, generateSecret

from apps.research.models import Participants, Spectators, StudyForm
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
        gform = GraphForm(request.POST, prefix="graph")
        sform = StudyForm(request.POST, prefix="study")
        if gform.is_valid() and (not gform.cleaned_data["study_active"] or sform.is_valid()):
            # woo all good, save the graph and build its concepts
            g = gform.save()
            g.build(gform.cleaned_data["graph_json"])

            # insert study data if applicable
            if gform.cleaned_data["study_active"]:
                s = sform.save(commit=False)
                s.graph = g
                s.save()

                # build participant list; final one is the spectator
                sid = None
                for n, pid in enumerate(sform.cleaned_data["pids"]):
                    sid = Participants(pid=pid, graph=g, linear=(n%2==1))
                    sid.save()

                # save the spectator
                Spectators(participant=sid, study=s).save()

            # all saved, forward to map
            return HttpResponseRedirect(reverse("maps:display", kwargs={"gid":g.pk}))
    else:
        gform = GraphForm(initial={'secret':generateSecret()}, prefix="graph")
        sform = StudyForm(prefix="study")

    return render(request, "maps-new.html", {'gform':gform,'sform':sform})

def edit(request, gid=""):
    return HttpResponse("editing a graph")

