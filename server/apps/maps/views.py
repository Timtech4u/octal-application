from django.core.urlresolvers import reverse
from django.forms import HiddenInput
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from models import Graphs, Concepts, GraphForm, KeyForm
from utils import graphCheck, GraphIntegrityError, generateSecret

from apps.research.models import Participants, Spectators, Studies, StudyForm
from apps.research.utils import getParticipantByUID, handleSurveys, urlLanding

import json

def display_all(request):
    graphs = Graphs.objects.filter(public=True).all()

    return render(request, "maps-all.html", {"maps":graphs})

def new_graph(request):
    f = {}
    if request.method == 'POST':
        # form submission
        f['graph'] = GraphForm(request.POST, prefix="graph")
        f['study'] = StudyForm(request.POST, prefix="study")
        if f['graph'].is_valid() and (not f['graph'].cleaned_data["study_active"] or f['study'].is_valid()):
            # woo all good, save the graph and build its concepts
            g = f['graph'].save()
            g.build(f['graph'].cleaned_data["graph_json"])

            # insert study data if applicable
            if f['graph'].cleaned_data["study_active"]:
                s = f['study'].save(commit=False)
                s.graph = g
                s.save()

                # build participant list; final one is the spectator
                p = None
                for n, pid in enumerate(f['study'].cleaned_data["pids"]):
                    p = Participants(pid=pid, study=s, linear=(n%2==1))
                    p.save()

                # spectators don't need to do pre- and post-surveys
                p.presurvey = True
                p.postsurvey = True
                p.linear = False
                p.save()

                # save the spectator
                Spectators(participant=p, study=s).save()
            else:
                # insert blank study
                Studies(graph=g).save()

            # all saved, forward to map
            return HttpResponseRedirect(reverse("maps:display", kwargs={"gid":g.pk}))
    else:
        f['graph'] = GraphForm(initial={'secret':generateSecret()}, prefix="graph")
        f['study'] = StudyForm(prefix="study")

    return render(request, "maps-form.html", {'forms':f})

def display(request, gid):
    graph = get_object_or_404(Graphs, pk=gid)

    #OCTAL experiment: graph linearity based on user id
    p = None
    linear = 1
    participant = 0

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
        participant = int(p.isParticipant())

    return render(request, "map.html",{"full_graph_skeleton":graph, 
                              "graph_name":graph.name,
                              "linear":linear,
                              "participant":participant,
                              "study_active": int(graph.study_active),})

def edit(request, gid=""):
    g = get_object_or_404(Graphs, pk=gid)
    s = get_object_or_404(Studies, pk=gid)

    f = {}

    if request.method == 'POST':
        f['key'] = KeyForm(request.POST, graph=g, prefix="key")
        if f['key'].is_valid():
            # user has entered a valid secret, save edited content or show form
            if f['key'].cleaned_data['edited']:
                f['graph'] = GraphForm(request.POST, instance=g, prefix="graph")
                f['study'] = StudyForm(request.POST, instance=s, prefix="study")

                if f['graph'].is_valid() and f['study'].is_valid():
                    return HttpResponse("yay")
            else:
                # prepare content; most data is provided by models
                f['key'] = KeyForm(graph=g, prefix="key",
                                   initial={'secret':g.secret,'edited':True})
                f['key'].fields["secret"].widget = HiddenInput()

                f['graph'] = GraphForm(instance=g, prefix="graph",
                                       initial={'graph_json':str(g)})
                
                pids = [p.pid for p in s.participants_set.all()]
                f['study'] = StudyForm(instance=s, prefix="study",
                                       initial={'pids':', '.join(pids)})
    else:
        f['key'] = KeyForm(graph=g, prefix="key")

    return render(request, "maps-form.html", {'forms':f, 'gid':gid})

