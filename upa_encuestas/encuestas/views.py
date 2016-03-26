from django.shortcuts import render,loader, HttpResponse, redirect
from django.contrib.auth import authenticate, login
from django.utils.html import escape
from django.template import RequestContext
from collections import defaultdict
import json, csv, io
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout



# Create your views here.
import numpy as np
from .models import Profesor, Clase, Encuesta

from . import Questionaire

# Upload form
@csrf_exempt
@login_required
def upload_file(request, en, en_type):

    content = request.FILES['file'].read()

    if en_type == "1":
        clase = Clase.objects.get(id = en)
        e = Encuesta(profesor = None, clase = clase, csv =content)
    else:
        profesor = Profesor.objects.get(id = en)
        e = Encuesta(profesor = profesor, clase = None, csv = content)
    e.save()
    return redirect('lista', en=str(en), en_type=str(en_type))
########

@login_required
def index(request):
    template = loader.get_template('encuestas/index.html')

    profesores = [(i.nombre,i.id) for i in Profesor.objects.all()]
    clases = [(i.nombre,i.id) for i in Clase.objects.all()]

    context = { 'profesores': profesores, 'clases': clases}
    return HttpResponse(template.render(context, request))

@login_required
def lista_encuestas(request, en, en_type):

    template = loader.get_template('encuestas/list.html')

    if en_type == "1": #clases. horrible, but works.
        nombre_clase = Clase.objects.get(id = en)
        encuestas = [(i.fecha_creacion,i.id) for i in Encuesta.objects.filter(clase = en).order_by('-fecha_creacion')]
        entity_name =nombre_clase.nombre 
    else:
        nombre_profesor = Profesor.objects.get(id = en)
        encuestas = [(i.fecha_creacion,i.id) for i in Encuesta.objects.filter(profesor = en).order_by('-fecha_creacion')]
        entity_name = nombre_profesor.nombre 

    if not encuestas:
        encuestas = list()

    context = {'entity_type': en_type, 'entity_id' : en, 'entity': entity_name, 'encuestas': encuestas}

    return HttpResponse(template.render(context, request))

@login_required
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


@login_required
def processEncuesta(request, encuesta):

    colours = [ '#5d8aa8', '#f0f8ff', '#e32636', '#efdecd', '#e52b50', '#ffbf00', '#ff033e', '#9966cc', '#a4c639', '#f2f3f4', '#cd9575', '#915c83', '#faebd7', '#008000', '#8db600', '#fbceb1', '#00ffff']

    transformation = {'Totalmente de acuerdo':10, 'Generalmente de acuerdo':7.5, 'Generalmente en desacuerdo':5, 'Totalmente en desacuerdo':1}

    #THIS IS UGLY as shit. This needs to go in the database so that we can configure it. But not now.
    user_comment = ['Nombre de usuario','P18. ¿Qué sugerencias tienes para mejorar el modulo?        ']

    template = loader.get_template('encuestas/results.html')
    #get the csv data from the database and start the parser.
    encuesta = Encuesta.objects.get(id = encuesta)
    #load the results

    csvdata = encuesta.csv
    reader = csv.DictReader(io.StringIO(csvdata),quotechar='"', dialect=csv.QUOTE_ALL, delimiter=',', lineterminator='\n')

    next(reader, None)  # skip the header
    #get the valid headers. This we will have to modify later in the future.
    valid = list()
    for i in (range(1,20)):
        valid.append('P'+str(i))
    #prepare for the values
    values = dict()
    #prepare for the students and the comments
    comments = list()
    students = list()
    student_score = list()
    for row in reader:
        #get the comments and such
        comments.append((row['Nombre de usuario'], row['P18. ¿Qué sugerencias tienes para mejorar el modulo?        ']))
        students.append(row['Nombre de usuario'])
        if row['P19. Por favor de una evaluacion simple del 1-10 de este modulo']:
            student_score.append(int(row['P19. Por favor de una evaluacion simple del 1-10 de este modulo']))
        for key in row.keys():
            if row[key] and (key.strip().split('.')[0] in valid) and row[key] in transformation.keys():
                if key in values:
                    values[key].append(transformation[row[key]])
                else:
                    values[key] = list()
    final_csv = list()
    for key in values.keys():
        if key.split('.')[0] in valid:
            final_csv.append({'weight': 1, 'score' : np.mean(values[key]), 'label': key, 'id':key.split('.')[0], 'color': colours[valid.index(key.split('.')[0])]})
    final_csv = json.dumps(final_csv)

    #now we need to get the comments and the students

    context = {'csv' : final_csv, 'student_score': np.mean(student_score), 'comments':comments, 'students': students}
    return HttpResponse(template.render(context, request))


def user_login(request):
    template = loader.get_template('encuestas/login.html')
    # Like before, obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        username = request.POST['username']
        password = request.POST['password']

        # Use Django's machinery to attempt to see if the username/password
        # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None (Python's way of representing the absence of a value), no user
        # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # If the account is valid and active, we can log the user in.
                # We'll send the user back to the homepage.
                login(request, user)
                return HttpResponseRedirect('/encuestas/')
            else:
                # An inactive account was used - no logging in!
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            return HttpResponse("Invalid login details supplied.")

    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the
        # blank dictionary object...
        return HttpResponse(template.render(context, request))


# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return HttpResponseRedirect('/encuestas/')
