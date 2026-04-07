from dataclasses import dataclass

@dataclass
class Pregunta:
    nombre_pregunta: str
    enunciado_pregunta: str
    nota_defecto: str
    penalizacion: str | None
    tipo: str

