import json

from django.http import HttpResponse
from lazysignup.decorators import allow_lazy_user
from django.contrib.auth.models import User

from apps.exercises.models import ExerciseAttempts

from apps.ki.utils import performInference

@allow_lazy_user
def knowledge_inference(request, gid="", conceptID=""):
    if request.method == "GET":
        u, uc = User.objects.get_or_create(pk=request.user.pk)
        p = getParticipantByUID(request.user.pk)

        # well, this shouldn't happen
        if p is None: return HttpResponse(status=401)

        ex = ExerciseAttempts.objects.filter(participant=p).filter(submitted=True)
        if not p.isParticipant(): ex = ex.filter(user=u)
        r = [e.get_correctness() for e in ex]
        inferences = performInference(r)
        return HttpResponse(json.dumps(inferences), mimetype='application/json')
    else:
        return HttpResponse(status=405)
