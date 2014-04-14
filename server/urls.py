import pdb
from django.conf.urls import patterns, include, url
# handle static files locally
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views.decorators.cache import cache_page
from django.views.generic.base import TemplateView, RedirectView

from views import OctalView

admin.autodiscover()

"""
Django urls handler
"""
urlpatterns = patterns('',
                       #url(r'^$', RedirectView.as_view(url="/concepts/midterm"), name='start'),
                       #url(r'^$', TemplateView.as_view(template_name="landing.html")),
                       url(r'^(?i)maps/', include('apps.maps.urls', namespace="maps")),
                       url(r'^(?i)octal/', include('apps.octal.urls', namespace="octal")),
                       url(r'^participant/', include('apps.participant.urls', namespace='part')),
)

urlpatterns += staticfiles_urlpatterns()
