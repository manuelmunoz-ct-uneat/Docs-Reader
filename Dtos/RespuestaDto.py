from dataclasses import dataclass

@dataclass
class RespuestaDto(dict):
    respuesta: str
    retroalimentacion: str