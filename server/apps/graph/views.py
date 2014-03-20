import json
import pdb

from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext

from apps.cserver_comm.cserver_communicator import get_full_graph_json_str, get_concept_data
from apps.user_management.models import Profile
from apps.participant.utils import getParticipantByUID, handleSurveys

def get_agfk_app(request):
    concepts = get_user_data(request)
    concept_tag = request.path.split("/")[-1].split("#")[0]
    concept_data = get_concept_data(concept_tag)
    # pdb.set_trace()
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

    return render_to_response("agfk-app.html",{
                              "full_graph_skeleton": get_full_graph_json_str(), 
                              "user_data": json.dumps(concepts),
                              "concept_data": concept_data,
                              "user_display": int(p.linear),
                              "pid": int(p.pid),
                              }, context_instance=RequestContext(request))


def get_graph_creator(request):
    concepts = get_user_data(request)
    full_graph_json = get_full_graph_json_str()
    return render_to_response("graph-creator.html", {"full_graph_skeleton": full_graph_json, "user_data": json.dumps(concepts)}, context_instance=RequestContext(request))

def get_user_data(request):
    if request.user.is_authenticated():
        uprof, created = Profile.objects.get_or_create(pk=request.user.pk)
        lset = set()
        sset = set()
        [lset.add(lc.id) for lc in uprof.learned.all()]
        [sset.add(sc.id) for sc in uprof.starred.all()]
        concepts = {"concepts": [{"id": uid, "learned": uid in lset, "starred": uid in sset} for uid in lset.union(sset)]}
    else:
        concepts = {"concepts": []}
    return concepts
