from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse

from models import Graphs, Concepts
from utils import graphCheck, GraphIntegrityError
from apps.research.utils import getParticipantByUID, handleSurveys

import json

def display_all(request):
    return HttpResponse("listing all graphs")

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
            return HttpResponseRedirect(reverse('maps:research:landing', kwargs={'gid':gid, 'err':''}))

        # make sure participant completed the presurvey
        r = handleSurveys(p, gid)
        if r is not None: return HttpResponseRedirect(r)

        linear = int(p.linear)
        pid = int(p.pid)

    return render_to_response("app.html",{
                              "full_graph_skeleton": graph, 
                              "graph_name": graph.name,
                              "user_display": linear,
                              "pid": pid,
                              "study_active": int(graph.study_active),
                              }, context_instance=RequestContext(request))

def new_graph(request):
    return HttpResponse("generate a new graph")

def build(request, gid=""):
    graph_json = '[{"id":"algorithmic_complexity","title":"Algorithmic Complexity","dependencies":[{"source":"lists"},{"source":"tail_recursion"},{"source":"tree_recursion"}]},{"id":"concurrency","title":"Concurrency","dependencies":[{"source":"functions"}]},{"id":"conditionals","title":"Conditionals","dependencies":[{"source":"variables"}]},{"id":"fractals","title":"Fractals","dependencies":[{"source":"tree_recursion"},{"source":"tail_recursion"}]},{"id":"functions","title":"Functions","dependencies":[{"source":"variables"}]},{"id":"lists","title":"Lists","dependencies":[{"source":"loops"}]},{"id":"loops","title":"Loops","dependencies":[{"source":"variable_mutation"},{"source":"conditionals"}]},{"id":"midterm","title":"Midterm","dependencies":[{"source":"algorithmic_complexity"},{"source":"fractals"},{"source":"concurrency"}]},{"id":"tail_recursion","title":"Tail Recursion","dependencies":[{"source":"functions"}]},{"id":"tree_recursion","title":"Tree Recursion","dependencies":[{"source":"functions"}]},{"id":"variable_mutation","title":"Variable Mutation","dependencies":[{"source":"variables"}]},{"id":"variables","title":"Variables","dependencies":[]}]'

    # no midterm leaf
    #graph_json = '[{"id":"algorithmic_complexity","title":"Algorithmic Complexity","dependencies":[{"source":"lists"},{"source":"tail_recursion"},{"source":"tree_recursion"}]},{"id":"concurrency","title":"Concurrency","dependencies":[{"source":"functions"}]},{"id":"conditionals","title":"Conditionals","dependencies":[{"source":"variables"}]},{"id":"fractals","title":"Fractals","dependencies":[{"source":"tree_recursion"},{"source":"tail_recursion"}]},{"id":"functions","title":"Functions","dependencies":[{"source":"variables"}]},{"id":"lists","title":"Lists","dependencies":[{"source":"loops"}]},{"id":"loops","title":"Loops","dependencies":[{"source":"variable_mutation"},{"source":"conditionals"}]},{"id":"tail_recursion","title":"Tail Recursion","dependencies":[{"source":"functions"}]},{"id":"tree_recursion","title":"Tree Recursion","dependencies":[{"source":"functions"}]},{"id":"variable_mutation","title":"Variable Mutation","dependencies":[{"source":"variables"}]},{"id":"variables","title":"Variables","dependencies":[]}]'
    # cyclic
    #graph_json = '[{"id":"algorithmic_complexity","title":"Algorithmic Complexity","dependencies":[{"source":"lists"},{"source":"tail_recursion"},{"source":"tree_recursion"}]},{"id":"concurrency","title":"Concurrency","dependencies":[{"source":"functions"}]},{"id":"conditionals","title":"Conditionals","dependencies":[{"source":"variables"}]},{"id":"fractals","title":"Fractals","dependencies":[{"source":"tree_recursion"},{"source":"tail_recursion"}]},{"id":"functions","title":"Functions","dependencies":[{"source":"variables"}]},{"id":"lists","title":"Lists","dependencies":[{"source":"loops"}]},{"id":"loops","title":"Loops","dependencies":[{"source":"variable_mutation"},{"source":"conditionals"}]},{"id":"midterm","title":"Midterm","dependencies":[{"source":"algorithmic_complexity"},{"source":"fractals"},{"source":"concurrency"}]},{"id":"tail_recursion","title":"Tail Recursion","dependencies":[{"source":"functions"}]},{"id":"tree_recursion","title":"Tree Recursion","dependencies":[{"source":"functions"}]},{"id":"variable_mutation","title":"Variable Mutation","dependencies":[{"source":"variables"},{"source":"loops"}]},{"id":"variables","title":"Variables","dependencies":[]}]'

    # orphaned concept
    #graph_json = '[{"id":"algorithmic_complexity","title":"Algorithmic Complexity","dependencies":[{"source":"lists"},{"source":"tail_recursion"},{"source":"tree_recursion"}]},{"id":"concurrency","title":"Concurrency","dependencies":[{"source":"functions"}]},{"id":"conditionals","title":"Conditionals","dependencies":[{"source":"variables"}]},{"id":"fractals","title":"Fractals","dependencies":[{"source":"tree_recursion"},{"source":"tail_recursion"}]},{"id":"functions","title":"Functions","dependencies":[{"source":"variables"}]},{"id":"lists","title":"Lists","dependencies":[{"source":"loops"}]},{"id":"loops","title":"Loops","dependencies":[{"source":"variable_mutation"},{"source":"conditionals"}]},{"id":"midterm","title":"Midterm","dependencies":[]},{"id":"tail_recursion","title":"Tail Recursion","dependencies":[{"source":"functions"}]},{"id":"tree_recursion","title":"Tree Recursion","dependencies":[{"source":"functions"}]},{"id":"variable_mutation","title":"Variable Mutation","dependencies":[{"source":"variables"}]},{"id":"variables","title":"Variables","dependencies":[]}]'

    # make a list of concepts from the json
    try:
        graph_list = json.loads(graph_json)
    except ValueError:
        return HttpResponse("Error: malformed JSON")

    try:
        concepts = graphCheck(graph_list)
    except GraphIntegrityError as e:
        return HttpResponse("Error: %s" % e.value)

    # graph checks out, let's insert it
    try:
        graph, new = Graphs.objects.get_or_create(pk=gid)
    except Graphs.DoesNotExist():
        return HttpResponse(status=404)

    if not new: graph.concepts_set.all().delete()

    def _build(cid):
        if "db" in concepts[cid]: return concepts[cid]["db"]
        db = Concepts(graph=graph, conceptId=cid, name=concepts[cid]["name"])
        db.save()
        for depid in concepts[cid]["deps"]:
            db.dependencies.add(_build(depid))
        concepts[cid]["db"] = db
        return db

    for c in concepts: _build(c)

    return HttpResponse("successful: %s" % graph)


