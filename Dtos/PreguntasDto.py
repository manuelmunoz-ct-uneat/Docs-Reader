from dataclasses import dataclass
from enum import Enum

@dataclass
class Pregunta:
    nombre_pregunta: str
    enunciado_pregunta: str
    nota_defecto: str
    penalizacion: str | None
    tipo: TipoDePregunta

class TipoDePregunta(Enum):
    OPCION_MULTIPLE = 1
    VERDADERO_FALSO = 2
    EMPAREJAMIENTO = 3
    ENSAYO = 4

