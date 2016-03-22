from django.shortcuts import render,loader, HttpResponse
from collections import defaultdict
import json

# Create your views here.
from .models import Profesor, Clase, Encuesta

from . import Questionaire

def index(request):
    template = loader.get_template('encuestas/index.html')

    profesores = [(i.nombre,i.id) for i in Profesor.objects.all()]
    clases = [(i.nombre,i.id) for i in Clase.objects.all()]

    context = { 'profesores': profesores, 'clases': clases}
    return HttpResponse(template.render(context, request))

def lista_encuestas_profesor(request, profesor):
    template = loader.get_template('encuestas/list_encuestas.html')
    nombre_profesor = Profesor.objects.get(id = profesor)

    encuestas = [(i.fecha_creacion,i.id) for i in Encuesta.objects.filter(profesor = profesor)]

    context = {'entity':' el Profesor ', 'entity_name':nombre_profesor.nombre, 'encuestas': encuestas}
    return HttpResponse(template.render(context, request))

def lista_encuestas_clase(request, clase):
    template = loader.get_template('encuestas/list_encuestas.html')

    nombre_clase = Clase.objects.get(id = clase)

    encuestas = [(i.fecha_creacion,i.id) for i in Encuesta.objects.filter(clase = clase)]

    context = {'entity':' la clase ', 'entity_name':nombre_clase, 'encuestas': encuestas}

    return HttpResponse(template.render(context, request))

def processEncuesta(request, encuesta):
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
        'understood_course':    'El curso logra hacerme entender la materia',
        'interest':     'El curso logra despertar mi interes hacia el contenido',
        'well_formulated_goals':        'Las metas de aprendizaje estan bien formuladas',
        'goals_and_activities_align':   'Hay una alineacion (relacion directa) entre las metas de aprendizaje y las actividades desarrolladas en clase',
        'objectives_communicated':      'Los objetivos de aprendizaje fueron comunicados claramente',
        'activities_correlate_evaluation':      'Las actividades del modulo me preparan para las evaluaciones',
        'clear_structure':      'La estructura del modulo es clara',
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

    values = defaultdict(list)

    #average student score "simple_evaluation"
    average_student_score = 0
    #comments  (tuple of student and comment) 
        #'username':     'Nombre de usuario',
        # 'suggestions'

    comments = list()
    #number of elements
    elements_in_questionaire = 0
    for elem in parser:
        elements_in_questionaire += 1
        #get the average student score
        try:
            average_student_score += int(elem.simple_evaluation)
        except:
            pass
        #get the comments
        try:
            comments.append((elem.username, elem.suggestions))
        except:
            pass

        for tag in tags:
            if getattr(elem, tag):
                values[tag].append(getattr(elem, tag))
            else:
                values[tag].append(0)

    
    #average the student score
    average_student_score /= 10.0

    json_data = list()
    composite_score = 0 
    for tag in tags:
        data = []
        for bin in [0,1,2,3,4]:
            data.append({'bin': bin, 'count':values[tag].count(bin)})
            #add the score to determine the composite score afterwards.
            composite_score += values[tag].count(bin)
            
        histogram = {'name': tags[tag], 'data':data}
        
        json_data.append(histogram)

    #the composite score is just the average score
    composite_score = composite_score / len(tags)


    #final json data.
    final_json = json.dumps(json_data)

    context = {'json':final_json, 'composite_score' : composite_score, 'student_score': average_student_score, 'comments':comments}

    return HttpResponse(template.render(context, request))
