from django.contrib import admin

from .models import Profesor, Clase, Encuesta
# Register your models here.

admin.site.register(Profesor)
admin.site.register(Clase)
admin.site.register(Encuesta)
