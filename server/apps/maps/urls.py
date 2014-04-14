from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView

from apps.maps import views
from apps.ki.views import knowledge_inference

urlpatterns = patterns('',
                       url(r'build$', views.build, name='build'),
                       url(r'map-(?P<gid>[0-9]*)', include([
                           url(r'^/exercises', include('apps.exercises.urls', namespace="exs")),
                           url(r'^/ki', knowledge_inference, name="ki"),
                           url(r'', views.display, name='display'),
                           ])),
)
