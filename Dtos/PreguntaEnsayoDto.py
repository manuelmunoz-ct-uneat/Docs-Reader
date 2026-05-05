from dataclasses import dataclass
from .PreguntasDto import PreguntaDto
from .RespuestaEnsayoDto import RespuestaEnsayoDto
from typing import Any

@dataclass
class PreguntaEnsayoDto(PreguntaDto):
    respuestas: RespuestaEnsayoDto

    def __init__(self, jsonData, id_pregunta, datosActividad):
        super().__init__(jsonData, id_pregunta, datosActividad)
        self.respuestas = RespuestaEnsayoDto.from_dict(jsonData.get('ops'))

    @classmethod
    def from_dict(cls, jsonData, id_pregunta, datosActividad):
        return cls(jsonData, id_pregunta, datosActividad)