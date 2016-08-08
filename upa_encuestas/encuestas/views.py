from django.shortcuts import render,loader, HttpResponse, redirect
from django.contrib.auth import authenticate, login
from django.utils.html import escape
from django.template import RequestContext
from collections import defaultdict
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt

import os
import gspread,math
from oauth2client.client import SignedJwtAssertionCredentials
import pandas as pd
import json,csv,io
import hashlib
import datetime



# Create your views here.
import numpy as np
from .models import Profesor, Clase, Encuesta

# Upload form
@csrf_exempt
#@login_required
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

#@login_required
@csrf_exempt
def index(request):
    template = loader.get_template('encuestas/index.html')

    profesores = [(i.nombre,i.id) for i in Profesor.objects.all()]
    clases = [(i.nombre,i.id) for i in Clase.objects.all()]

    context = { 'profesores': profesores, 'clases': clases}
    return HttpResponse(template.render(context, request))

#@login_required
@csrf_exempt
def syncEncuestas(request):

    file_dir = os.path.dirname(__file__)  # get current directory

    SCOPE = ["https://spreadsheets.google.com/feeds"]
    SECRETS_FILE = os.path.join(file_dir,"Encuestas-6752894900ec.json")

    json_key = json.load(open(SECRETS_FILE))
    # Authenticate using the signed key
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'], SCOPE)
    gc = gspread.authorize(credentials)
    #get the year for the current encuestas
    now = datetime.datetime.now()
    cur_year = str(now.year)
    for sheet in gc.openall():
        sheet_title = sheet.title
        if sheet_title.strip().split('.')[0] == "Prof":
            continue
        else:
            workbook = gc.open(sheet_title)
            # Get the first sheet
            sheet = workbook.sheet1
            # Extract all data into a dataframe
            data = pd.DataFrame(sheet.get_all_records())
            #check if it is prof. encuestas or class encuesta
            #this is important because we first create all the classes.
            #the name comes as: Introduccion a la computacion (Responses). So, we need the Introduccion a la computacion alone
            encuesta_name = sheet_title.strip().split('(')[0].strip()
            #try to get the clase_object, if it exists.
            try:
                clase_object = Clase.objects.get(nombre = encuesta_name)
            except:
            #the clase already exists, and so we just add the encuesta
                #the clase does not exist, so just create a new one.
                clase_object = Clase(nombre = encuesta_name)
                clase_object.save()

            #get all the encuestas for this particular clase. we sort it based on year. so we only check if the last one changed
            #becuase this is the one we are interested in. That is, the logic works as the class is an independent entity.
            encuestas = list([i for i in Encuesta.objects.filter(clase = clase_object.id).order_by('-fecha_creacion')])
            #check for duplicated encuestas.
            if len(encuestas) > 0:
                if hashlib.sha224(encuestas[-1].csv.encode('utf-8')).hexdigest() != hashlib.sha224(data.to_csv().encode('utf-8')).hexdigest():
                    new_encuesta = Encuesta(profesor = None, clase = clase_object, csv = data.to_csv())
                    new_encuesta.save()
            else:
                new_encuesta = Encuesta(profesor = None, clase = clase_object, csv = data.to_csv())
                new_encuesta.save()

        #process the profesores sheet
    for sheet in gc.openall():
        sheet_title = sheet.title
        #we need to skip the ones thata are not for professors.
        if sheet_title.strip().split('.')[0] != "Prof":
            continue
        workbook = gc.open(sheet_title)
        # Get the first sheet
        sheet = workbook.sheet1
        # Extract all data into a dataframe
        data = pd.DataFrame(sheet.get_all_records())
        #the name comes as: Prof. Horacio Caniza_Introduccion a la computacion (Responses). So, we need the Horacio Caniza alone
        profesor_name = sheet_title.strip().split('.')[1].split('(')[0].strip()
        profesor_name = profesor_name.split('_')[0].strip()
        #get the name of the class this professor is teaching.
        current_clase = sheet_title.strip().split('_')[1].split('(')[0].strip()
        try:
            profesor_object = Profesor.objects.get(nombre = profesor_name)
        except:
            #if we have not found the profesor, then we do nothing, we just continue and add the new encuesta
            profesor_object = Profesor(nombre = profesor_name)
            profesor_object.save()

        #now we need to get the clase object for this particular professor.
        #this has to exist, we have made sure. If it fails, its because I made a mistake creating the 
        #forms.
        current_clase_object = Clase.objects.get(nombre = current_clase)

        #we fetch the latest encuesta and if it is the same (hash of the entire record) do not save.
        encuestas = list([i for i in Encuesta.objects.filter(profesor = profesor_object.id, clase= current_clase_object.id).order_by('-fecha_creacion')])
        if len(encuestas) > 0:
            if hashlib.sha224(encuestas[-1].csv.encode('utf-8')).hexdigest() != hashlib.sha224(data.to_csv().encode('utf-8')).hexdigest():
                new_encuesta = Encuesta(profesor = profesor_object, clase = current_clase_object, csv = data.to_csv())
                new_encuesta.save()
        else:
            new_encuesta = Encuesta(profesor = profesor_object, clase = current_clase_object, csv = data.to_csv())
            new_encuesta.save()


    return HttpResponse(json.dumps({'Success':'Ok'}), content_type="application/json")
            

#@login_required
def lista_materias_profesor(request, en):
    template = loader.get_template('encuestas/list.html')
    profesor = Profesor.objects.get(id = en)

    profesor_clases = [i.clase for i in Encuesta.objects.filter(profesor = profesor)]

    entity_name = profesor.nombre 

    #now we need to get the class ids to get all the classnames.
    clases = list()
    for clase_id in profesor_clases:
        clases.extend([(i.nombre,i.id) for i in Clase.objects.filter(id = clase_id.id)])

    context = {'entity_type': "2", 'entity_id' : en, 'entity': entity_name, 'clases':clases}


    return HttpResponse(template.render(context, request))


#@login_required
def lista_encuestas(request, en, en2):

    template = loader.get_template('encuestas/list.html')

    #clases. horrible, but works.
    if en2 == "-1": 
        nombre_clase = Clase.objects.get(id = en)
        encuestas = [(i.fecha_creacion,i.id) for i in Encuesta.objects.filter(clase = en).order_by('-fecha_creacion')]
        entity_name =nombre_clase.nombre 
    else:
        nombre_clase = Clase.objects.get(id = en)
        nombre_profesor = Profesor.objects.get(id = en2)
        encuestas = [(i.fecha_creacion,i.id) for i in Encuesta.objects.filter(clase = en , profesor = en2).order_by('-fecha_creacion')]
        entity_name = nombre_profesor.nombre 

    #nothing was found
    if not encuestas:
        encuestas = list()
        sorted_encuestas = list()
    else:
        #store in dictionary, to organize in years.
        sorted_encuestas = list()
        for enc in encuestas:
            encuesta = {'year' : enc[0].year, 'value':enc[0], 'id': enc[1]}
            sorted_encuestas.append(encuesta)


    context = {'entity_type': "1", 'entity_id' : en, 'entity': entity_name, 'encuestas': encuestas, 'sorted_encuestas':sorted_encuestas}

    return HttpResponse(template.render(context, request))


#@login_required
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

def processEncuestaPandas(encuesta, valid_questions):
    transformation = {'Totalmente de acuerdo':10, 'Generalmente de acuerdo':7.5, 'Generalmente en desacuerdo':5, 'Totalmente en desacuerdo':1, 'Si':10, 'No':5}

    encuesta = Encuesta.objects.get(id = encuesta)
    #load the results
    csvdata = encuesta.csv
    reader = pd.read_csv(io.StringIO(csvdata), quotechar = '"', delimiter = ',', lineterminator = '\n',index_col=0)
    #here we check whether it is a professor or a module
    if not encuesta.profesor:#clase
        en_type = '1'
        column_names = {'P1. Los objetivos de aprendizaje del módulo son comprensibles':'objectivos_comprensibles',
                 'P2. El curso logra hacerme entender la materia':'logra_hacerme_entender',
                 'P3. El curso logra despertar mi interés hacia el contenido':'despertar_interes',
                 'P4. Las metas de aprendizaje están bien formuladas':'metas_bien_formuladas',
                 'P5. Hay una alineación (relación directa) entre las metas de aprendizaje y las actividades desarrolladas en clase':'alineacion',
                 'P6. Los objetivos de aprendizaje fueron comunicados claramente':'objetivos_claros',
                 'P7. Las actividades del módulo me preparan para las evaluaciones':'preparan_para_evaluacion',
                 'P8. Se comunico el contenido del modulo al inicio de clases':'contenido_comunicado',
                 'P9. La estructura del módulo es clara':'estructura_clara',
                 'P10. Las temáticas son relevantes para su área de estudio o trabajo':'tematica_relevante',
                 'P11. El contenido se adapta al área de estudio o trabajo': 'contenido_adaptado',
                 'P12. Hay un balance entre teoría y práctica':'balance_teoria',
                 'P13. La metodología de enseñanza esta orientada hacia el desarrollo de competencias':'competencias',
                 'P14. La documentación y los materiales educativos son útiles para alcanzar los objetivos del módulo':'materiales_utiles',
                 'P15. La documentación y los materiales educativos fueron entregados a tiempo': 'materiales_a_tiempo',
                 'P16. La forma de evaluación es conocida':'evaluacion_conocida',
                 'P17. ¿Cuál es la lección mas importante de este módulo?':'leccion_mas_importante',
                 'P18. ¿Qué sugerencias tienes para mejorar el módulo?':'sugerencias',
                 'P19. Por favor de una evaluacion simple del 1-10 de este módulo':'evaluacion_simple',
                 '¿Cuál fue el motivo principal para llevar este módulo?':'motivo', 
                 '¿Lograste el objetivo del módulo?':'objetivo_logrado',
                 'Sexo':'sexo','Timestamp':'timestamp', 'Username':'username'}

        #replace the names with simpler ones.
        reader.rename(columns=column_names, inplace=True)

        #these columns require special treamtmen
        exclude_columns = ['objetivo_logrado', 'sugerencias','sexo','leccion_mas_importante', 'timestamp','username', 'evaluacion_simple', 'motivo']

        #here we store the simple evaluation and various comments made by the students.
        student_score = [i for i in reader['evaluacion_simple'] if not math.isnan(float(i))]
        comments = [[i for i in reader['username']], [i for i in reader['sugerencias']], [i for i in reader['leccion_mas_importante']], [i for i in reader['objetivo_logrado']]]
        students_comments = {z[0]:list(z[1:]) for z in zip(*comments)}


    else: #profesor.
        en_type = '2'
        column_names  = {'P1. El Profesor esta bien preparado para las clases':'preparado',
                   'P2. El Profesor domina la parte teórica del módulo ':'domina_teoria',
                   'P3. El Profesor tiene suficiente experiencia práctica en la temática ':'domina_practica',
                   'P4. El Profesor aplica una metodología que ayuda a entender contenidos y cuestiones complejas':'metodologia',
                   'P5. El Profesor motiva a través de una metodología interactiva ':'motiva_interactiva',
                   'P6. El Profesor utiliza suficientes casos prácticos':'casos_practicos',
                   'P7. El Profesor aplica suficientes trabajos en grupo':'trabajos_en_grupo',
                   'P8. El Profesor esta disponible para atender consultas':'disponible',
                   'P9. El trato entre el Profesor y los estudiantes refleja respeto mutuo ':'respeto',
                   'P10. Por favor de una evaluacion simple del 1-10 de este profesor':'evaluacion_simple',
                   '¿Que le ha gustado y que sugerencias tiene Usted para el Profesor?':'sugerencias',
                   'Timestamp':'timestamp', 'Username':'username'}
        #replace the names with simpler ones.
        reader.rename(columns=column_names, inplace=True)

        exclude_columns = ['evaluacion_simple', 'sugerencias','timestamp','username']

        #check for nan.. this will not happen in fugure queries where this is checked.

        student_score = [i for i in reader['evaluacion_simple'] if not math.isnan(float(i))]

        comments = [[i for i in reader['username']], [i for i in reader['sugerencias']]]
        students_comments = {z[0]:list(z[1:]) for z in zip(*comments)}

    #reverse the column names just to have them for labels in the graph.
    inv_column_names = {v: k for k, v in column_names.items()}
    #preapare for the values.
    values = defaultdict(list)
    for column in [i for i in list(reader) if i not in exclude_columns]:
        #the question will always come, but it might happen that one of the questions was not made mandatory, an so we get a nan. we need to skip.
        values[inv_column_names[column]].extend([transformation[j] for j in reader[column] if j in transformation])

    return (values,student_score, students_comments, en_type)


#@login_required
def processEncuesta(request, encuesta):
    template = loader.get_template('encuestas/results.html')
    colours = [ '#5d8aa8', '#f0f8ff', '#e32636', '#efdecd', '#e52b50', '#ffbf00', '#ff033e', '#9966cc', '#a4c639', '#f2f3f4', '#cd9575', '#915c83', '#faebd7', '#008000', '#8db600', '#fbceb1', '#00ffff']

    #get the valid headers. This we will have to modify later in the future.
    valid = list()
    for i in (range(1,20)):
        valid.append('P'+str(i))

    #(values,student_score, students,comments) =  __processEncuesta(encuesta, valid)
    (values,student_score, comments, en_type) =  processEncuestaPandas(encuesta, valid)

    final_csv = list()
    i = 0
    for i, key in enumerate(values.keys()):
        if key.split('.')[0] in valid:

            final_csv.append({'weight': 1, 'score' : np.mean(values[key]), 'label': key, 'id':key.split('.')[0], 'color': colours[i]})
    final_csv = json.dumps(final_csv)

    #context = {'csv' : final_csv, 'student_score': np.mean(student_score),'en_id':encuesta, 'comments':comments, 'students': students}
    context = {'en_type':en_type,'csv' : final_csv, 'student_score': np.mean(student_score),'en_id':encuesta, 'comments':comments, 'students': list(comments.keys())}
    return HttpResponse(template.render(context, request))

def details(request, encuesta):
    template = loader.get_template('encuestas/details.html')
    #get the valid headers. This we will have to modify later in the future.
    valid = list()
    for i in (range(1,20)):
        valid.append('P'+str(i))

    #Data Used for this example...
    #var dataSet1 = [
    #  {legendLabel: "Legend String 1", magnitude: 54, link: "http://www.if4it.com/SYNTHESIZED/DISCIPLINES/Visualization_Management_Home_Page.html"},

    encuesta = Encuesta.objects.get(id = encuesta)
    #load the results
    csvdata = encuesta.csv
    reader = csv.DictReader(io.StringIO(csvdata),quotechar='"', dialect=csv.QUOTE_ALL, delimiter=',', lineterminator='\n')
    next(reader, None)  # skip the header
    json_data = list()
    choices = ['Totalmente de acuerdo', 'Generalmente de acuerdo', 'Generalmente en desacuerdo', 'Totalmente en desacuerdo']
    collected_scores = defaultdict()
    for row in reader:
        #get the comments and such
        for id_key in row.keys():
            key = id_key.strip().split('.')[0]
            if (key in valid):
                if not key in collected_scores:
                    collected_scores[key] = list()
                if row[id_key] and row[id_key] in choices:
                    collected_scores[key].append(row[id_key])

    values = list()
    for key in collected_scores:
        histogram = defaultdict(list)
        for choice in choices:
            histogram[key].append({'legendLabel': choice, 'magnitude': collected_scores[key].count(choice)})
        values.append(histogram)


#    (values,x,x, x) =  __processEncuesta(encuesta,valid)
#    json_data = list()
#    composite_score = 0 
#    for tag in values.keys():
#        data = []
#        for bin in [1,5,7.5,10]:
#            data.append({'legendLabel': tag, 'magnitude':values[tag].count(bin), 'link':'#'})
#            #add the score to determine the composite score afterwards.
#            composite_score += values[tag].count(bin)
#        histogram = {'title': tag , 'data':data}
#        json_data.append(histogram)
    #the composite score is just the average score
    final_json = json.dumps(values)

    context = {'json' : final_json}
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
def elements(request):
    template = loader.get_template('encuestas/elements.html')
    return HttpResponse(template.render({}, request))

#@login_required
def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)
    # Take the user back to the homepage.
    return HttpResponseRedirect('/encuestas/')
