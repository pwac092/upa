from django.shortcuts import render,loader, HttpResponse, redirect
from collections import defaultdict
import json

# Create your views here.
import numpy as np
from .models import Profesor, Clase, Encuesta

from . import Questionaire

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
        encuestas = [(i.fecha_creacion,i.id) for i in Encuesta.objects.filter(clase = en)]
        entity_name = ' la clase ' + nombre_clase.nombre + ' '
    else:
        nombre_profesor = Profesor.objects.get(id = en)
        encuestas = [(i.fecha_creacion,i.id) for i in Encuesta.objects.filter(profesor = en)]
        entity_name = ' el Profesor ' + nombre_profesor.nombre + ' '

    if not encuestas:
        encuestas = list()

    context = {'entity_type': en_type, 'entity': entity_name, 'encuestas': encuestas}

    return HttpResponse(template.render(context, request))

def add(request):
    pass

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

    colors = {
        'comprehensible_objectives':    '#FF99FF', 
        'understood_course':            '#FFFF00', 
        'interest':                     '#33CCCC', 
        'well_formulated_goals':        '#CCCC99', 
        'goals_and_activities_align':   '#99FF33', 
        'objectives_communicated':      '#CCCC99', 
        'activities_correlate_evaluation': '#33CCCC',
        'clear_structure':              '#FF9966', 
        'relevant_themes':              '#66CC99', 
        'relevant_content':             '#999999', 
        'theory_practice_balance':      '#CC66CC', 
        'comptence_methodology':        '#99CC99', 
        'available_documentation':      '#00CCFF', 
        'documentation_on_time':        '#FF9966', 
        'evaluation_is_understood':     '#FFCC00', 
        'most_important_lesson':        '#00FF99'}

    tags = {
        #'timestamp':    'Marca temporal',
        #'username':     'Nombre de usuario',
        #'course':       'Curso',
        #'date':      'Fecha',
        #'sex':  'Femenino o Masculino',
        #'age':  'Edad',
        #'education':    'Nivel mas alto de formacion',
        #'motive':       'Cual fue el motivo principal para llevar este modulo?',
        #'objective_achieve':    'Lograste el objetivo del modulo?',
        #'objective_achieve_reason':     'Si se han logrado o no logrado los objetivos puedes explicar por que?',
        'comprehensible_objectives':    'Los objetivos de aprendizaje del modulo son comprensibles',
        'understood_course':            'El curso logra hacerme entender la materia',
        'interest':                     'El curso logra despertar mi interes hacia el contenido',
        'well_formulated_goals':        'Las metas de aprendizaje estan bien formuladas',
        'goals_and_activities_align':   'Hay una alineacion (relacion directa) entre las metas de aprendizaje y las actividades desarrolladas en clase',
        'objectives_communicated':      'Los objetivos de aprendizaje fueron comunicados claramente',
'activities_correlate_evaluation':      'Las actividades del modulo me preparan para las evaluaciones',
        'clear_structure':              'La estructura del modulo es clara',
                'relevant_themes':      'Las tematicas son relevantes para su area de estudio o trabajo',
                'relevant_content':     'El contenido es suficientemente adaptado al area de estudio o trabajo',
        'theory_practice_balance':      'Hay un balance entre teoria y practica?',
        'comptence_methodology':        'La metodologia de ensenanza esta orientada hacia el desarrollo de competencias?',
        'available_documentation':      'La documentacion y los materiales educativos son utiles para alcanzar los objetivos del modulo?',
        'documentation_on_time':        'La documentacion y los materiales educativos fueron entregados a tiempo?',
        'evaluation_is_understood':     'La forma de evaluacion es conocida?',
        'most_important_lesson':        'Cual es la leccion mas importante de este modulo?'}
        #'suggestions':  'Que sugerencias tienes para mejorar el modulo?',}
        #'simple_evaluation':    'Por favor de una evaluacion simple del 1-10 de este modulo'}
    template = loader.get_template('encuestas/results.html')
    #get the csv data from the database and start the parser.
    encuesta = Encuesta.objects.get(id = encuesta)
    parser = Questionaire.QuestionaireFile(encuesta.csv)

    #average student score "simple_evaluation"
    average_student_score = list()
    #comments  (tuple of student and comment) 
        #'username':     'Nombre de usuario',
        # 'suggestions'
    comments = list()
    for elem in parser:
        #get the average student score. Nobody is supposed to be able to 
        #get away with no filling this out, but there we go.
        try:
            average_student_score.append(int(elem.simple_evaluation))
        except:
            pass
        #get the comments. Same thing here as before, just a matter of finding those that can 
        #be filled.
        try:
            comments.append((elem.username, elem.suggestions))
        except:
            pass
        #For the individual comments, same thing goes here. We will add only those that
        #exist, the otherones, we will ignore.
        values = defaultdict(list)
        for tag in tags:
            if getattr(elem, tag):
                values[tag].append(float(getattr(elem, tag)))
            else:
                pass
        csv = list()
        
        for tag in tags:
            csv.append({'weight':1, 'score' : 25, 'label': tags[tag], 'id':tag, 'color': colors[tag]})

    #csv = [{'weight': '0.5', 'color': '#9E0041', 'label': 'Fisheries', 'score': '59', 'order': '1.1', 'id': 'FIS'}, {'weight': '0.5', 'color': '#C32F4B', 'label': 'Mariculture', 'score': '24', 'order': '1.3', 'id': 'MAR'}, {'weight': '1', 'color': '#E1514B', 'label': 'Artisanal Fishing Opportunities', 'score': '98', 'order': '2', 'id': 'AO'}, {'weight': '1', 'color': '#F47245', 'label': 'Natural Products', 'score': '60', 'order': '3', 'id': 'NP'}, {'weight': '1', 'color': '#FB9F59', 'label': 'Carbon Storage', 'score': '74', 'order': '4', 'id': 'CS'}, {'weight': '1', 'color': '#FEC574', 'label': 'Coastal Protection', 'score': '70', 'order': '5', 'id': 'CP'}, {'weight': '1', 'color': '#FAE38C', 'label': 'Tourism &  Recreation', 'score': '42', 'order': '6', 'id': 'TR'}, {'weight': '0.5', 'color': '#EAF195', 'label': 'Livelihoods', 'score': '77', 'order': '7.1', 'id': 'LIV'}, {'weight': '0.5', 'color': '#C7E89E', 'label': 'Economies', 'score': '88', 'order': '7.3', 'id': 'ECO'}, {'weight': '0.5', 'color': '#9CD6A4', 'label': 'Iconic Species', 'score': '60', 'order': '8.1', 'id': 'ICO'}, {'weight': '0.5', 'color': '#6CC4A4', 'label': 'Lasting Special Places', 'score': '65', 'order': '8.3', 'id': 'LSP'}, {'weight': '1', 'color': '#4D9DB4', 'label': 'Clean Waters', 'score': '71', 'order': '9', 'id': 'CW'}, {'weight': '0.5', 'color': '#4776B4', 'label': 'Habitats', 'score': '88', 'order': '10.1', 'id': 'HAB'}, {'weight': '0.5', 'color': '#5E4EA1', 'label': 'Species', 'score': '83', 'order': '10.3', 'id': 'SPP'}]
    #here we build the barchart.

    #json_data = list()
    #for tag in tags:
        #data = []
        #for bin in [0,1,2,3,4]:
            #data.append({'bin': bin, 'count':values[tag].count(bin)})
        #histogram = {'name': tags[tag], 'data':data}
        #json_data.append(histogram)
    #final json data.
    #final_json = json.dumps(json_data)

    final_csv = json.dumps(csv)

    context = {'csv' : final_csv, 'student_score': average_student_score, 'comments':comments}

    return HttpResponse(template.render(context, request))
