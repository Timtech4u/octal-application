from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from lazysignup.decorators import allow_lazy_user

from apps.participant.models import Participants, ParticipantLogins
from apps.user_management.models import Profile
from apps.participant.utils import getParticipantByPID, getParticipantByUID, presurveyRedirect 

@allow_lazy_user
def landing(request, err=0):
    return render_to_response("octal-landing.html", 
                              {"err":err},
                              context_instance=RequestContext(request))



@allow_lazy_user
def handle_pid(request, pid=0):
    # check that the pid is valid
    p = getParticipantByPID(pid)

    if p is None:
        return HttpResponseRedirect("/participant/1")

    # a participant may use the tool from multiple browsers
    uprof, created = Profile.objects.get_or_create(pk=request.user.pk)

    # remember the participant's lazy signup id to rebuild progress
    ParticipantLogins.objects.get_or_create(participant=p, uprofile=uprof)

    # has the user completed the presurvey yet?
    if not p.presurvey:
        return presurveyRedirect(p)

    return HttpResponseRedirect("/")

def presurvey(request):
    p = None
    if request.user.is_authenticated():
        p = getParticipantByUID(request.user.pk)

    if p is None:
        return HttpResponseRedirect("/participant/")

    p.presurvey = True
    p.save()

    return HttpResponseRedirect("/")
