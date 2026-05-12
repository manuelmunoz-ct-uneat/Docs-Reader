from Dtos.PreguntaOpcionMultipleDto import PreguntaOpcionMultipleDto
from Dtos.PreguntaEmparejamientoDto import PreguntaEmparejamientoDto
from Dtos.PreguntaVerdaderoFalsoDto import PreguntaVerdaderoFalsoDto
from Dtos.PreguntaEnsayoDto import PreguntaEnsayoDto
from Dtos.CourseDataDto import CourseDataDto
import re

class Mapper():

    @staticmethod
    def procesarCurso(course_route):
        courseCodeRegex = r'^[A-Z]{2,4}\d{3,4}$'
        courseActivityType = {'co', 'rec01', 'rec02', 'test', 'tarea'}
        courseActivityLang = {'esp', 'ing', 'fra', 'por'}
        
        course_route = str(course_route)
        course = course_route[(course_route.rfind('\\')+1):course_route.rfind('.')].split('-')
        course[len(course)-1] = course[len(course)-1].split('_')[0]

        courseData = CourseDataDto

        for data in course:
            if re.match(courseCodeRegex, data):
                courseData.courseId =  data
            elif data.lower() in courseActivityType:
                courseData.courseActv = data
            elif data.lower() in courseActivityLang:
                courseData.courseLang = data.lower()

        return courseData
    

    @classmethod
    def tipoPregunta(cls, courseData, dataJson):
        
        preguntasDeActividad = []
        datosActividad = cls.procesarCurso(courseData)
        preguntasDeActividad.append(datosActividad)
        
        for numPregunta, data in dataJson.items():
            if data.get("tipo") == "multi":
                preguntaMultiple = PreguntaOpcionMultipleDto.from_dict(data, numPregunta, datosActividad)
                preguntasDeActividad.append(preguntaMultiple)
            elif data.get("tipo") == "match":
                preguntaEmparejamiento = PreguntaEmparejamientoDto.from_dict(data, numPregunta, datosActividad)
                preguntasDeActividad.append(preguntaEmparejamiento)
            elif data.get("tipo") == "V/F":
                preguntaVerdaderoFalso = PreguntaVerdaderoFalsoDto.from_dict(data, numPregunta, datosActividad)
                preguntasDeActividad.append(preguntaVerdaderoFalso)
            elif data.get("tipo") == "ensayo":
                preguntaEnsayo = PreguntaEnsayoDto.from_dict(data, numPregunta, datosActividad)
                preguntasDeActividad.append(preguntaEnsayo)
        
        return preguntasDeActividad


