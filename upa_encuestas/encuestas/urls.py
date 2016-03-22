from django.conf.urls import url

from . import views

urlpatterns = [
            url(r'^$', views.index, name='index'),
            url(r'^lista_clase/(?P<clase>\d+)/$', views.lista_encuestas_clase, name='lista_clase'),
            url(r'^lista_prof/(?P<profesor>\d+)/$', views.lista_encuestas_profesor,name='lista_profesor'),
            url(r'^process/(?P<encuesta>\d+)/$', views.processEncuesta,name='process'),
            ]
