from Dtos.OpcionMultipleDto import OpcionMultipleDto
from Dtos.PreguntasDto import Pregunta
from Dtos.RespuestaDto import RespuestaDto
import re


class Mapper():


    @staticmethod
    def procesarCurso(course_route) -> dict[str, str]:
        courseCodeRegex = r'^[A-Z]{2,3}\d{3,4}$'
        courseActivityType = {'co', 'rec01', 'rec02', 'test', 'tarea'}
        courseActivityLang = {'esp', 'ing', 'fra', 'por'}
        
        course_route = str(course_route)
        course = course_route[(course_route.rfind('\\')+1):course_route.rfind('.')].split('-')
        course[len(course)-1] = course[len(course)-1].split('_')[0]

        courseData = {}

        for data in course:
            if re.match(courseCodeRegex, data):
                courseData.update({'courseId': data})

            elif data.lower() in courseActivityType:
                courseData.update({'courseActv': data})

            elif data.lower() in courseActivityLang:
                courseData.update({'courseLang': data})


        return courseData
    


    @classmethod
    def tipoPregunta(cls, course_data, dataJson):
        datos = []
        datosActividad = cls.procesarCurso(course_data)
        datos.append(datosActividad)
        for id_pregunta, data in dataJson.items():
            if data.get("tipo") == "multi":
                multi_pregunta = OpcionMultipleDto.from_dict(data, id_pregunta, datosActividad)
                datos.append(multi_pregunta)
            elif data.get("tipo") == "match":

                print("Pregunta match")
            elif data.get("tipo") == "ensayo":
                print("Pregunta ensayo")
            elif data.get("tipo") == "V/F":
                print("Pregunta V/F")
        
        return datos


