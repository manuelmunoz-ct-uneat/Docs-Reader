from dataclasses import dataclass

@dataclass
class RespuestaDto(dict):
    pregunta: str
    retroalimentacion: str