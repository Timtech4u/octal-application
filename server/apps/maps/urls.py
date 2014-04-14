from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from apps.maps import views

urlpatterns = patterns('',
                       url(r'build$', views.build, name='build'),
                       url(r'map-(?P<gid>[0-9]*)', views.display, name='display'),
                      )
