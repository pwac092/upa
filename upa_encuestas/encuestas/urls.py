from django.conf.urls import url

from . import views

urlpatterns = [
            url(r'^$', views.index, name='index'),
            url(r'^lista/(?P<en>\d+)/(?P<en_type>\d+)/$', views.lista_encuestas, name='lista'),
            url(r'^process/(?P<encuesta>\d+)/$', views.processEncuesta,name='process'),
            url(r'^add/$', views.add,name='add'),
            url(r'^delete/(?P<encuesta>\d+)/(?P<en>\d+)/$', views.delete,name='delete'),
            ]
