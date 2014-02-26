from apps.user_management.models import Profile
from apps.participant.models import Participants, ParticipantLogins
from django.http import HttpResponse, HttpResponseRedirect

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

def presurveyRedirect(p):
    #TODO change to surveymonkey link - can we pass in pid?
    return HttpResponseRedirect("http://cnn.com") 
