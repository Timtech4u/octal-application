from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView

from apps.exercises import views

urlpatterns = patterns('',
                       url(r'^fetch/(?P<conceptId>[^/]*)/(?P<qid>[0-9]*)$',
                           views.fetch_ex, name='getexercise'),
                       url(r'^attempt/(?P<attempt>[^/]*)/(?P<correct>[01])$', 
                           views.attempt, name='addattempt'),
                       url(r'^build', views.build, name='buildexercises'),
                      )
