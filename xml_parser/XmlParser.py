from Dtos import (PreguntaEnsayoDto, PreguntaEmparejamientoDto, PreguntaOpcionMultipleDto, PreguntaVerdaderoFalsoDto)
from.QuestionsXml import QuestionXml

class XmlParser:
    
    @staticmethod
    def parse(questions: list):
        xmlDocument = ""

        for question in questions:
            if isinstance(question, PreguntaEmparejamientoDto):
                preguntaEmparejamiento = QuestionXml.prguntaEmparejamiento(question)
                xmlDocument += preguntaEmparejamiento
            elif isinstance(question, PreguntaEnsayoDto):
                print(questions)
            elif isinstance(question, PreguntaOpcionMultipleDto):
                cantidadCorrectas = sum(1 for op in question.respuestas.respuestas.values() if op.ok is True)
                preguntaMulti = QuestionXml.preguntaOpcionMultiple(question, cantidadCorrectas)
                xmlDocument += preguntaMulti
            elif isinstance(question, PreguntaVerdaderoFalsoDto):
                print("mayhaps")
            else:
                print("crear nueva seccion de preguntas")
                

        with open("documento_xml.xml", "w", encoding="utf-8") as file:
            file.write(xmlDocument)
            