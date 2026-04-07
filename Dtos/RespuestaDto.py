from dataclasses import dataclass

@dataclass
class Respuesta(dict):
    pregunta: str
    retroalimentacion: str