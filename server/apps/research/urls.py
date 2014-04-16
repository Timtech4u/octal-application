from django.conf.urls import patterns, url
from django.views.generic.base import RedirectView

from . import views

urlpatterns = patterns('',
                       url(r'^(?P<err>[0-9]*)$', views.landing, name='landing'),
                       url(r'^pid/(?P<pid>[a-zA-Z0-9]*)/?$', views.handle_pid, name='handlepid'),
                       url(r'^presurvey/?$', views.presurvey, name='presurvey'),
                       url(r'^postsurvey/?$', views.postsurvey, name='postsurvey'),
                       url(r'^complete/?$', views.complete, name='complete'),
                       url(r'^logout/?', views.logout, name='logout'),
                      )
