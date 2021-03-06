from django.conf.urls import url

from . import views

urlpatterns = [
            url(r'^$', views.index, name='index'),

            url(r'^lista/(?P<en>\d+)/(?P<en2>-?\d+)/$', views.lista_encuestas, name='lista'),

            url(r'^listaProfesores/(?P<en>\d+)/$', views.lista_materias_profesor, name='listaProfesores'),
            url(r'^process/(?P<encuesta>\d+)/$', views.processEncuesta,name='process'),
            url(r'^details/(?P<encuesta>\d+)/$', views.details,name='details'),
            url(r'^delete/(?P<encuesta>\d+)/(?P<en>\d+)/$', views.delete,name='delete'),
            url(r'^upload/(?P<en>\d+)/(?P<en_type>\d+)/$', views.upload_file, name='upload'),
            url(r'^login/$', views.user_login, name='login'),
            url(r'^logout/$', views.user_logout, name='logout'),
            url(r'^sync/$', views.syncEncuestas , name='sync'),
            url(r'^elements/$', views.elements, name='elements'),

            ]
