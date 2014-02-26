from django.conf.urls import patterns, url
from django.views.generic.base import TemplateView, RedirectView

from apps.participant import views

urlpatterns = patterns('',
                       url(r'^pid/(?P<pid>\d{5})$', views.handle_pid, name='handlepid'),
                       url(r'^pid/', RedirectView.as_view(url='/?piderror')),
                      )
