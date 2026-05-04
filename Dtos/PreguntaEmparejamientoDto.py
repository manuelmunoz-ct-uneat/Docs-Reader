from dataclasses import dataclass
from .PreguntasDto import PreguntaDto
from .RespuestaEmparejamientoDto import RespuestaEmparejamientoDto

@dataclass
class PreguntaEmparejamientoDto(PreguntaDto):

    respuestas: RespuestaEmparejamientoDto

    def __init__(self, jsonData, numeroPregunta, datosActividad):
        super().__init__(jsonData, numeroPregunta, datosActividad)

        self.respuestas = RespuestaEmparejamientoDto.from_dict(jsonData.get("ops"))

    @classmethod
    def from_dict(cls, data, id_pregunta, datosActividad):
        return cls(data, id_pregunta, datosActividad)

