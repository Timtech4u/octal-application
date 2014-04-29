from django.conf.urls import patterns, url, include
from django.views.generic.base import TemplateView

from apps.maps import views
from apps.ki.views import knowledge_inference

urlpatterns = patterns('',
                       url(r'^/?$', views.display_all, name='display_all'),
                       url(r'^/new/?', views.new_graph, name='new'),
                       url(r'^/(?P<gid>[0-9]+)', include(patterns('',
                           url(r'^/edit/?$', views.edit, name='edit'),
                           url(r'^/exercises', include('apps.exercises.urls', namespace="exercises")),
                           url(r'^/ki/?$', knowledge_inference, name="ki"),
                           url(r'^/lti/?$', views.lti, name='lti'),
                           url(r'^/research', include('apps.research.urls', namespace='research')),
                           url(r'', views.display, name='display'),
                           ))),
)
