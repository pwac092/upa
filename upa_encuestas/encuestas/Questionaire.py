"""
=======
License
=======

Copyright (c) 2009 Tamas Nepusz <tamas@cs.rhul.ac.uk>
Copyright (c) 2011 Horacio Caniza <h.j.canizavierci@cs.rhul.ac.uk>

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

__author__  = "Horacio Caniza"
__email__   = "h.j.canizavierci@cs.rhul.ac.uk"
__copyright__ = "Copyright (c) 2011, Tamas Nepusz"
__license__ = "MIT"
__version__ = "0.1"

__all__ = ["Questionaire", "QuestionaireFile"]

from collections import deque, namedtuple

class StudentAnswer(object):
    """Class representing a questionaire (possibly parsed from an
    annotation file). Two types of questionaire exist: A course questionaire
    and a teacher questionaire.
    """
        # {
        #    'timestamp':    'Marca temporal',
        #    'username':     'Nombre de usuario',
        #    'course':       'Curso',
        #    'date':      'Fecha',
        #    'sex':  'Femenino o Masculino',
        #    'age':  'Edad',
        #    'education':    'Nivel mas alto de formacion',
        #    'motive':       'Cual fue el motivo principal para llevar este modulo?',
        #    'objective_achieve':    'Lograste el objetivo del modulo?',
        #    'objective_achieve_reason':     'Si se han logrado o no logrado los objetivos puedes explicar por que?',
        #    'comprehensible_objectives':    'Los objetivos de aprendizaje del modulo son comprensibles',
        #    'understood_course':    'El curso logra hacerme entender la materia',
        #    'interest':     'El curso logra despertar mi interes hacia el contenido',
        #    'well_formulated_goals':        'Las metas de aprendizaje estan bien formuladas',
        #    'goals_and_activities_align':   'Hay una alineacion (relacion directa) entre las metas de aprendizaje y las actividades desarrolladas en clase',
        #    'objectives_communicated':      'Los objetivos de aprendizaje fueron comunicados claramente',
        #    'activities_correlate_evaluation':      'Las actividades del modulo me preparan para las evaluaciones',
        #    'clear_structure':      'La estructura del modulo es clara',
        #    'relevant_themes':      'Las tematicas son relevantes para su area de estudio o trabajo',
        #    'relevant_content':     'El contenido es suficientemente adaptado al area de estudio o trabajo',
        #    'theory_practice_balance':      'Hay un balance entre teoria y practica?',
        #    'comptence_methodology':        'La metodologia de ensenanza esta orientada hacia el desarrollo de competencias?',
        #    'available_documentation':      'La documentacion y los materiales educativos son utiles para alcanzar los objetivos del modulo?',
        #    'documentation_on_time':        'La documentacion y los materiales educativos fueron entregados a tiempo?',
        #    'evaluation_is_understood':     'La forma de evaluacion es conocida?',
        #    'most_important_lesson':        'Cual es la leccion mas importante de este modulo?',
        #    'suggestions':  'Que sugerencias tienes para mejorar el modulo?',
        #    'simple_evaluation':    'Por favor de una evaluacion simple del 1-10 de este modulo'}

    __slots__ = ['timestamp', 'username', 'course', 'date', 'sex', 'age', 'education',
                'motive', 'objective_achieve', 'objective_achieve_reason', 'comprehensible_objectives',
                'understood_course', 'interest', 'well_formulated_goals', 'goals_and_activities_align',
                'objectives_communicated', 'activities_correlate_evaluation', 'clear_structure',
                'relevant_themes', 'relevant_content', 'theory_practice_balance', 'comptence_methodology',
                'available_documentation', 'documentation_on_time', 'evaluation_is_understood', 'most_important_lesson',
                'suggestions', 'simple_evaluation']


    #__slots__ = ["db", "db_object_id", "db_object_symbol", \
            #"qualifiers", "go_id", "db_references", \
            #"evidence_code", "with", "aspect", \
            #"db_object_name", "db_object_synonyms", \
            #"db_object_type", "taxons", "date", \
            #"assigned_by", "organism_name"]

    def __init__(self, *args):
        """Constructs an annotation. Use keyword arguments to specify the values
        of the different attributes. If you use positional arguments, the order
        of the arguments must be the same as they are in the GO annotation file.
        No syntax checking is done on the values entered, but attributes with a
        maximum cardinality more than one are converted to lists automatically.
        (If you specify a string with vertical bar separators as they are in the
        input file, the string will be splitted appropriately)."""

        choices = {'Totalmente de acuerdo' :4, 'Generalmente de acuerdo':3, 'Generalmente en desacuerdo' : 2, 'Totalmente en desacuerdo':1}

        if len(args) == 1:
            args = args[0].strip().split("\t")

        for (name, value) in zip(self.__slots__, args):
            numeric_value = None
            if value in choices:
                value = choices[value]
            #translate the values
            setattr(self, name, value)

        for name in self.__slots__:
            if not hasattr(self, name):
                setattr(self, name, "")

    def __repr__(self):
        params = ",".join("%s=%r" % (name, getattr(self, name)) \
                for name in self.__slots__)
        return "%s(%s)" % (self.__class__.__name__, params)


class QuestionaireFile(object):
    """A parser class that processes questionaire files"""

    def __init__(self, fp):
        """Creates an file parser that reads the given file-like
        object. 

          >>> import upa_questionaire as upa
          >>> parser = upa.QuestionaireFile("fisica_2.csv")

        To read the answers in the file, you must iterate over the parser
        as if it were a list. The iterator yields `StudentAnswer` objects.
        """
        self.fp = fp
        self.lineno = 0

    def answers(self):
        """Iterates over the annotations in this annotation file,
        yielding an `Annotation` object for each annotation."""
        for line in self.fp:
            self.lineno += 1
            if not line:
                # This is a comment line
                continue
            try:
                yield StudentAnswer(line)
            except (TypeError):
                raise ParseError("cannot parse questionaire", self.lineno)

    def __iter__(self):
        return self.answers()

