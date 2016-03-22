from django.db import models

# Create your models here.

class Profesor(models.Model):
    def __str__(self):
        return self.nombre
    nombre = models.CharField(max_length=200)

class Clase(models.Model):
    def __str__(self):
        return self.nombre

    nombre = models.CharField(max_length=200)

class Encuesta(models.Model):

    profesor = models.ForeignKey(Profesor, null=True)
    clase = models.ForeignKey(Clase, null=True)
    #La encuesta.
    csv = models.TextField()
    fecha_creacion = models.DateField(auto_now_add=True)
