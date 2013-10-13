from django.conf.urls import patterns, url

from camm import views


urlpatterns = patterns('',
    url(r'^$', views.SimulationType.as_view()),
    url(r'^simulation_form/$', views.simulation_form),
    url(r'^submit/$', views.submit),
)

