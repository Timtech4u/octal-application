from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from lazysignup.decorators import allow_lazy_user

from models import Participants, Logins
from utils import getParticipantByPID, getParticipantByUID, handleSurveys, participantLogout, urlLanding, urlHome, urlComplete, require_study_active

@require_study_active
@allow_lazy_user
def landing(request, gid="", err=0):
    return render_to_response("study-landing.html", 
                              {"err":err},
                              context_instance=RequestContext(request))

@require_study_active
@allow_lazy_user
def complete(request, gid=""):
    participantLogout(request.user, gid)
    return render_to_response("study-complete.html",
                              context_instance=RequestContext(request))


@require_study_active
@allow_lazy_user
def logout(request, gid=""):
    participantLogout(request.user, gid)
    return HttpResponseRedirect(urlHome(gid))

@require_study_active
@allow_lazy_user
def handle_pid(request, gid="", pid=""):
    # check that the pid is valid
    p = getParticipantByPID(pid)

    if p is None:
        return HttpResponseRedirect(urlLanding(gid, '1'))

    # a participant may use the tool from multiple browsers
    u, created = User.objects.get_or_create(pk=request.user.pk)

    # remember the participant's lazy signup id to rebuild progress
    Logins.objects.get_or_create(participant=p, user=u)

    # redirect to pre- or post-survey, as appropriate
    redirect = handleSurveys(p)

    if redirect is None:
        if p.study.complete and p.isParticipant():
            redirect = urlComplete(gid)
        else:
            redirect = urlHome(gid)

    return HttpResponseRedirect(redirect)

@require_study_active
def presurvey(request, gid=""):
    p = None
    if request.user.is_authenticated():
        p = getParticipantByUID(request.user.pk)

    if p is None:
        return HttpResponseRedirect(urlLanding(gid))

    p.presurvey = True
    p.save()

    return HttpResponseRedirect(urlHome(gid))

@require_study_active
def postsurvey(request, gid=""):
    if not STUDY_COMPLETE:
        return HttpResponseRedirect(redirectHome(gid))

    p = None
    if request.user.is_authenticated():
        p = getParticipantByUID(request.user.pk)

    if p is None:
        return HttpResponseRedirect(urlLanding(gid))

    p.postsurvey = True
    p.save()

    return HttpResponseRedirect(urlComplete(gid))
