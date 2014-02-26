from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from apps.participant import views

urlpatterns = patterns('',
                       url(r'^(?P<err>[0-9]*)$', views.landing, name='landing'),
                       url(r'^pid/(?P<pid>\d{5})$', views.handle_pid, name='handlepid'),
                       url(r'^pid/', RedirectView.as_view(url='/participant/1')),
                       url(r'^presurvey/$', views.presurvey, name='presurvey'),
                      )
