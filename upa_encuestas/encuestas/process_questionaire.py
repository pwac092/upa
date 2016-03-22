


import Questionaire

import numpy as np
import matplotlib.pyplot as plt

    
    tags = 
         {
            'timestamp':    'Marca temporal',
            'username':     'Nombre de usuario',
            'course':       'Curso',
            'date':      'Fecha',
            'sex':  'Femenino o Masculino',
            'age':  'Edad',
            'education':    'Nivel mas alto de formacion',
            'motive':       'Cual fue el motivo principal para llevar este modulo?',
            'objective_achieve':    'Lograste el objetivo del modulo?',
            'objective_achieve_reason':     'Si se han logrado o no logrado los objetivos puedes explicar por que?',
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
            'most_important_lesson':        'Cual es la leccion mas importante de este modulo?',
            'suggestions':  'Que sugerencias tienes para mejorar el modulo?',
            'simple_evaluation':    'Por favor de una evaluacion simple del 1-10 de este modulo'}

    

if __name__ == "__main__":
    #read file
    parser = Questionaire.QuestionaireFile('../fisica1.tsv')
    for elem in parser:

