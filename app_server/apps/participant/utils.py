from apps.user_management.models import Profile
from apps.participant.models import Participants, ParticipantLogins
from django.http import HttpResponse, HttpResponseRedirect

STUDY_COMPLETE = True

def getParticipantByUID(uid):
    uprof, created = Profile.objects.get_or_create(pk=uid)
    try:
        p = ParticipantLogins.objects.filter(uprofile=uprof).get()
    except ParticipantLogins.DoesNotExist:
        return None
    return p.participant 

def getParticipantByPID(p):
    try:
        return Participants.objects.filter(pid=p).get()
    except Participants.DoesNotExist:
        return None

def participantLogout(user):
    p = None
    if user.is_authenticated():
        p = getParticipantByUID(user.pk)

    if p is None:
        return False

    uprof, created = Profile.objects.get_or_create(pk=user.pk)
    ParticipantLogins.objects.filter(participant=p, uprofile=uprof).delete()
    return True

def presurveyRedirect(p):
    return HttpResponseRedirect("https://www.surveymonkey.com/s/BLDLBCW?c="+p.pid) 

def postsurveyRedirect(p):
    return HttpResponseRedirect("https://www.surveymonkey.com/s/DQTNRZ6?c="+p.pid)

def handleSurveys(p):
    # has the user completed the presurvey yet?
    if not p.presurvey:
        # force users to presurvey while study is ongoing
        if not STUDY_COMPLETE:
            return presurveyRedirect(p)

        # if the study has completed and no presurvey, they cannot participate
        p.presurvey = True
        p.postsurvey = True
        p.save()
        return HttpResponseRedirect("/participant/complete")

    # only force postsurvey when study is complete
    if STUDY_COMPLETE and not p.postsurvey:
        return postsurveyRedirect(p)

    return None


