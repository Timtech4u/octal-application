from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from lazysignup.decorators import allow_lazy_user

from models import Logins, Studies, Spectators
from utils import getParticipantByPID, getParticipantByUID, handleSurveys, participantLogout, urlLanding, urlHome, urlComplete, require_study_active

@require_study_active
@allow_lazy_user
def landing(request, gid="", err=0):
    if getParticipantByUID(request.user.pk, gid) is not None:
        return HttpResponseRedirect(urlHome(gid))

    try:
        s = Spectators.objects.get(study=gid)
    except Spectators.DoesNotExist:
        return HttpResponse(status=404)
    return render_to_response("research-landing.html", 
                              {"gid":gid,"sid":s.pid,"err":err},
                              context_instance=RequestContext(request))

@require_study_active
@allow_lazy_user
def complete(request, gid=""):
    try:
        s = Spectators.objects.get(study=gid)
    except Spectators.DoesNotExist:
        return HttpResponse(status=404)

    if not s.complete:
        return HttpResponseRedirect(urlHome(gid))

    participantLogout(request.user, gid)
    return render_to_response("research-complete.html", 
                              {"gid":gid, "sid":s.pid},
                              context_instance=RequestContext(request))


@require_study_active
@allow_lazy_user
def logout(request, gid=""):
    participantLogout(request.user, gid)
    return HttpResponseRedirect(urlLanding(gid))

@require_study_active
@allow_lazy_user
def handle_pid(request, gid="", pid=""):
    try:
        s = Studies.objects.get(graph__pk=gid)
    except Studies.DoesNotExist:
        return HttpResponse(status=404)

     # check that the pid is valid
    p = getParticipantByPID(pid, gid)

    if p is None:
        return HttpResponseRedirect(urlLanding(gid, '1'))

    # a participant may use the tool from multiple browsers
    u, created = User.objects.get_or_create(pk=request.user.pk)

    # remember the participant's lazy signup id to rebuild progress
    Logins.objects.get_or_create(participant=p, user=u, study=s)

    # redirect to pre- or post-survey, as appropriate
    redirect = handleSurveys(p, gid)

    if redirect is None:
        if s.complete and p.isParticipant():
            redirect = urlComplete(gid)
        else:
            redirect = urlHome(gid)

    return HttpResponseRedirect(redirect)

@require_study_active
def presurvey(request, gid=""):
    p = getParticipantByUID(request.user.pk, gid)

    if p is None:
        return HttpResponseRedirect(urlLanding(gid))

    p.presurvey = True
    p.save()

    return HttpResponseRedirect(urlHome(gid))

@require_study_active
def postsurvey(request, gid=""):
    try:
        s = Studies.objects.get(graph__pk=gid)
    except Studies.DoesNotExist:
        return HttpResponse(status=404)

    if not s.complete:
        return HttpResponseRedirect(urlHome(gid))

    p = getParticipantByUID(request.user.pk, gid)

    if p is None:
        return HttpResponseRedirect(urlLanding(gid))

    p.postsurvey = True
    p.save()

    return HttpResponseRedirect(urlComplete(gid))
