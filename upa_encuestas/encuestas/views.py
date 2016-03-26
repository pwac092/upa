from django.shortcuts import render,loader, HttpResponse, redirect
from django.utils.html import escape
from collections import defaultdict
import json, csv
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
import numpy as np
from .models import Profesor, Clase, Encuesta

from . import Questionaire

# Upload form
@csrf_exempt
def upload_file(request, en, en_type):
    content = str(request.FILES['file'].read())
    if en_type == "1":
        clase = Clase.objects.get(id = en)
        e = Encuesta(profesor = None, clase = clase, csv =content)
    else:
        profesor = Profesor.objects.get(id = en)
        e = Encuesta(profesor = profesor, clase = None, csv = content)
    e.save()
    return redirect('lista', en=str(en), en_type=str(en_type))
########

def index(request):
    template = loader.get_template('encuestas/index.html')

    profesores = [(i.nombre,i.id) for i in Profesor.objects.all()]
    clases = [(i.nombre,i.id) for i in Clase.objects.all()]

    context = { 'profesores': profesores, 'clases': clases}
    return HttpResponse(template.render(context, request))

def lista_encuestas(request, en, en_type):

    template = loader.get_template('encuestas/list.html')

    if en_type == "1": #clases. horrible, but works.
        nombre_clase = Clase.objects.get(id = en)
        encuestas = [(i.fecha_creacion,i.id) for i in Encuesta.objects.filter(clase = en).order_by('-fecha_creacion')]
        entity_name = ' la clase ' + nombre_clase.nombre + ' '
    else:
        nombre_profesor = Profesor.objects.get(id = en)
        encuestas = [(i.fecha_creacion,i.id) for i in Encuesta.objects.filter(profesor = en).order_by('-fecha_creacion')]
        entity_name = ' el Profesor ' + nombre_profesor.nombre + ' '

    if not encuestas:
        encuestas = list()

    context = {'entity_type': en_type, 'entity_id' : en, 'entity': entity_name, 'encuestas': encuestas}

    return HttpResponse(template.render(context, request))

def delete(request, encuesta, en):
    #get the clase and profesor this encuesta belongs to.

    encuesta = Encuesta.objects.get(id = encuesta)

    if en == "1":
        entity = encuesta.clase.id
    else:
        entity = encuesta.profesor.id

    encuesta.delete()

    context = {'en': str(entity), 'entity_type':str(en)}
    return redirect('lista', en=str(entity), en_type=str(en))


def processEncuesta(request, encuesta):

    colours = [ '#5d8aa8', '#f0f8ff', '#e32636', '#efdecd', '#e52b50', '#ffbf00', '#ff033e', '#9966cc', '#a4c639', '#f2f3f4', '#cd9575', '#915c83', '#faebd7', '#008000', '#8db600', '#fbceb1', '#00ffff']

    transformation = {'Totalmente de acuerdo':4, 'Generalmente de acuerdo':3, 'Generalmente en desacuerdo':2, 'Totalmente en desacuerdo':1}

    template = loader.get_template('encuestas/results.html')
    #get the csv data from the database and start the parser.
    encuesta = Encuesta.objects.get(id = encuesta)
    #load the results

    csvdata = encuesta.csv
    reader = csv.DictReader(csvdata,quotechar='"', dialect=csv.QUOTE_ALL)
    next(reader, None)  # skip the header
    #get the valid headers. This we will have to modify later in the future.
    valid = list()
    for i in (range(1,20)):
        valid.append('P'+str(i))
    #prepare for the values
    values = defaultdict(list)
    for row in reader:
        for key in row.keys():
            if key.strip().split('.')[0] in valid:   
                transformed_value = process_file_value(row[key])
                if row[key]:
                    if row[key] in transformation.keys():
                        values[key].append(transformation[row[key]])

    for key in values.keys():
        if key.split('.')[0] in headers:
            csv.append({'weight':1, 'score' : np.mean(values[key]), 'label': escape(key), 'id':key.split('.')[0], 'color': tags[int(key.split('.')[0][2:])]})

    final_csv = json.dumps(csv)

    context = {'csv' : final_csv, 'student_score': average_student_score, 'comments':comments, 'students':students}
    return HttpResponse(template.render(context, request))
