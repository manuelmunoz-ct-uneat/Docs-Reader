from dataclasses import dataclass

@dataclass
class Pregunta:
    nombre_pregunta: str
    enunciado_pregunta: str
    tipo: str
    nota_defecto: str
    penalizacion: str
    img: str | None

