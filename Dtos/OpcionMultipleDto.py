from dataclasses import dataclass
from Dtos.PreguntasDto import Pregunta
from Dtos.RespuestaDto import RespuestaDto

@dataclass
class OpcionMultipleDto(Pregunta):
    respuestas: RespuestaDto

    def __init__(self, jsonData, id_pregunta, datosActividad):
        super().__init__(jsonData, id_pregunta, datosActividad)
        self.respuestas = RespuestaDto.from_dict(jsonData.get('ops'))

    @classmethod
    def from_dict(cls, jsonData, id_pregunta, datosActividad):
        return cls(jsonData, id_pregunta, datosActividad)



