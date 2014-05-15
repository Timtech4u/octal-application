import json

from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from apps.exercises.models import Attempts
from apps.maps.models import Graphs

from apps.ki.utils import performInference
from apps.research.utils import getParticipantByUID, studyFilter

def knowledge_inference(request, gid=""):
    if request.method == "GET":
        g = get_object_or_404(Graphs, pk=gid)

        if not request.user.is_authenticated(): return HttpResponse(status=403)
        u, uc = User.objects.get_or_create(pk=request.user.pk)
        p = getParticipantByUID(request.user.pk, gid)
        if g.study_active and p is None: return HttpResponse(status=401)

        ex = Attempts.objects.filter(graph=g).filter(submitted=True)
        ex = studyFilter(g, p, u, ex)
 
        inferences = []
        if ex.count() > 1:
            r = [e.get_correctness() for e in ex]
            inferences = performInference(g.concept_dict, r)
        return HttpResponse(json.dumps(inferences), mimetype='application/json')
    else:
        return HttpResponse(status=405)
