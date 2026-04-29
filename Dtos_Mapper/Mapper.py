from Dtos.OpcionMultipleDto import OpcionMultipleDto
from Dtos.PreguntasDto import Pregunta
from Dtos.RespuestaDto import RespuestaDto


class Mapper():

    @staticmethod
    def tipoPregunta(dataJson):
        datos = []
        for id_pregunta, data in dataJson.items():
            if data.get("tipo") == "multi":
                multi_pregunta = OpcionMultipleDto.from_dict(data, id_pregunta)
                datos.append(multi_pregunta)
            elif data.get("tipo") == "match":
                print("Pregunta match")
            elif data.get("tipo") == "ensayo":
                print("Pregunta ensayo")
            elif data.get("tipo") == "V/F":
                print("Pregunta V/F")
