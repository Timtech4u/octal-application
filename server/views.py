import json
import pdb

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from os import system

from apps.participant.utils import getParticipantByUID, handleSurveys

from forms import ContactForm


def OctalView(request):
    concept_tag = request.path.split("/")[-1].split("#")[0]

    #OCTAL experiment: graph linearity based on user id
    p = None
    if request.user.is_authenticated():
        p = getParticipantByUID(request.user.pk)

    #user has no participant ID yet, ask them for it
    if p is None:
        return HttpResponseRedirect('/participant/')

    # make sure participant completed the presurvey
    r = handleSurveys(p)
    if r is not None: return r

    return render_to_response("app.html",{
                              "full_graph_skeleton": get_full_graph_json_str(), 
                              "user_display": int(p.linear),
                              "pid": int(p.pid),
                              }, context_instance=RequestContext(request))

"""
Main application views that do not nicely fit into an app, i.e. because they span
multiple apps or are app agnostic
"""

class ContactView(FormView):
    template_name = 'feedback.html'
    form_class = ContactForm
    success_url = '/thanks'

    def form_valid(self, form):
        form.send_email()
        return super(ContactView, self).form_valid(form)
