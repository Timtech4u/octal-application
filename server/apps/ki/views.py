import json

from django.http import HttpResponse
from lazysignup.decorators import allow_lazy_user
from django.contrib.auth.models import User

from apps.exercises.models import Attempts
from apps.maps.models import Graphs

from apps.ki.utils import performInference
from apps.participant.utils import getParticipantByUID

@allow_lazy_user
def knowledge_inference(request, gid=""):
    if request.method == "GET":
        try:
            graph = Graphs.objects.get(pk=gid)
        except Graphs.DoesNotExist:
            return HttpResponse(status=422)
        u, uc = User.objects.get_or_create(pk=request.user.pk)
        p = getParticipantByUID(request.user.pk)

        # well, this shouldn't happen
        if p is None: return HttpResponse(status=401)

        ex = Attempts.objects.filter(participant=p).filter(submitted=True)
        if not p.isParticipant(): ex = ex.filter(user=u)
        inferences = []
        if ex.count() > 1:
            r = [e.get_correctness() for e in ex]
            inferences = performInference(graph.concept_dict, r)
        return HttpResponse(json.dumps(inferences), mimetype='application/json')
    else:
        return HttpResponse(status=405)
