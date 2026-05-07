from Dtos import (PreguntaEnsayoDto, PreguntaEmparejamientoDto, PreguntaOpcionMultipleDto, PreguntaVerdaderoFalsoDto)
from .QuestionsXml import QuestionXml

class XmlParser:
    
    @staticmethod
    def parse(questions: list):
        xmlDocument = ""

        for question in questions:
            if isinstance(question, PreguntaEmparejamientoDto):
                preguntaEmparejamiento = QuestionXml.prguntaEmparejamiento(question)
                xmlDocument += preguntaEmparejamiento
                
            elif isinstance(question, PreguntaEnsayoDto):
                preguntaEnsayo = QuestionXml.preguntaEnsayo(question)
                xmlDocument += preguntaEnsayo

            elif isinstance(question, PreguntaOpcionMultipleDto):
                cantidadCorrectas = sum(1 for op in question.respuestas.respuestas.values() if op.ok is True)
                preguntaMulti = QuestionXml.preguntaOpcionMultiple(question, cantidadCorrectas)
                xmlDocument += preguntaMulti

            elif isinstance(question, PreguntaVerdaderoFalsoDto):
                preguntaVerdaderoFalso = QuestionXml.preguntaVerdaderoFalso(question)
                xmlDocument += preguntaVerdaderoFalso

            else:
                print("crear nueva seccion de preguntas") # Se cambia la categoria de la seccion, ej CO -> E0, Rec01 -> R1 ...
                

        with open("documento_xml.xml", "w", encoding="utf-8") as file:
            file.write(xmlDocument)
            