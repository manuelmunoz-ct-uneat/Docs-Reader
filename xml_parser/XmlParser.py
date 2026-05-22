from Dtos import (PreguntaEnsayoDto, PreguntaEmparejamientoDto, PreguntaOpcionMultipleDto, PreguntaVerdaderoFalsoDto)
from .MoodleXml import MoodleXml

class XmlParser:
    
    @staticmethod
    def parse(questions: list):
        xmlDocument = "<quiz>\n"

        for question in questions:
            if isinstance(question, PreguntaEmparejamientoDto):
                preguntaEmparejamiento = MoodleXml.prguntaEmparejamiento(question)
                xmlDocument += preguntaEmparejamiento
                
            elif isinstance(question, PreguntaEnsayoDto):
                preguntaEnsayo = MoodleXml.preguntaEnsayo(question)
                xmlDocument += preguntaEnsayo

            elif isinstance(question, PreguntaOpcionMultipleDto):
                cantidadCorrectas = sum(1 for op in question.respuestas.respuestas.values() if op.ok is True)
                preguntaMulti = MoodleXml.preguntaOpcionMultiple(question, cantidadCorrectas)
                xmlDocument += preguntaMulti

            elif isinstance(question, PreguntaVerdaderoFalsoDto):
                preguntaVerdaderoFalso = MoodleXml.preguntaVerdaderoFalso(question)
                xmlDocument += preguntaVerdaderoFalso

            else:
                xmlDocument += MoodleXml.crearNuevaCategoria(question)
                
        xmlDocument += "</quiz>"
        return xmlDocument
            