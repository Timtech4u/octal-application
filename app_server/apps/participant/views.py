from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from lazysignup.decorators import allow_lazy_user

from apps.participant.models import ParticipantIDs, Participant
from apps.user_management.models import Profile

def handle_pid(request, pid=0):
    
    #TODO change to surveymonkey link - can we pass in pid?
    return HttpResponseRedirect("http://cnn.com") 
