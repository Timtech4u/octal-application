import pdb

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from os import system

from django.views.generic.edit import FormView

from apps.cserver_comm.cserver_communicator import get_search_json
from forms import ContactForm


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
