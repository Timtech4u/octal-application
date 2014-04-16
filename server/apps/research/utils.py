from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from models import Studies, Participants, Logins

from apps.maps.models import Graphs

def require_study_active(view):
    """
    A decorator that enforces study views are only visible for an active study
    """
    def _wrapped_view(request, gid, *args, **kwargs):
        g = None
        try:
            g = Graphs.objects.get(pk=gid)
        except Graphs.DoesNotExist: pass

        if g is None or not g.study_active:
            return HttpResponseRedirect(urlHome(gid))
        return view(request, gid, *args, **kwargs)
    return _wrapped_view


def studyFilter(g, p, u, query):
    """
    Filter a query based on a graph's study status
    """
    if g.study_active:
        query = query.filter(participant=p)
    if not g.study_active or not p.isParticipant():
        query = query.filter(user=u)
    return query

def getParticipantByUID(uid, gid):
    u, created = User.objects.get_or_create(pk=uid)

    try:
        s = Studies.objects.get(graph=gid)
    except Studies.DoesNotExist:
        return None

    try:
        p = Logins.objects.filter(study=s).get(user=u)
    except Logins.DoesNotExist:
        return None

    return p.participant 

def getParticipantByPID(p, gid):
    try:
        s = Studies.objects.get(graph=gid)
    except Studies.DoesNotExist:
        return None

    try:
        return Participants.objects.filter(study=s).get(pid=p)
    except Participants.DoesNotExist:
        return None

def participantLogout(user, gid):
    p = None
    if user.is_authenticated():
        p = getParticipantByUID(user.pk, gid)

    if p is None: return False

    u, created = User.objects.get_or_create(pk=user.pk)
    Logins.objects.filter(participant=p).filter(user=u).delete()
    return True

def urlHome(gid):
    return reverse('maps:display', kwargs={'gid':gid})

def urlLanding(gid, err=""):
    return reverse('maps:study:landing', kwargs={'gid':gid, 'err':err})

def urlComplete(gid):
    return reverse('maps:study:complete', kwargs={'gid':gid})

def presurveyRedirect(p):
    return HttpResponseRedirect("https://www.surveymonkey.com/s/BLDLBCW?c="+p.pid) 

def postsurveyRedirect(p):
    return HttpResponseRedirect("https://www.surveymonkey.com/s/DQTNRZ6?c="+p.pid)

def handleSurveys(p, gid):
    # has the user completed the presurvey yet?
    if not p.presurvey:
        # force users to presurvey while study is ongoing
        if not p.study.complete:
            return p.study.preSurveyURL(p.pid)

        # if the study has completed and no presurvey, they cannot participate
        p.presurvey = True
        p.postsurvey = True
        p.save()
        return urlComplete(gid)

    # only force postsurvey when study is complete
    if p.study.complete and not p.postsurvey:
        return p.study.postSurveyURL(p.pid)

    return None


