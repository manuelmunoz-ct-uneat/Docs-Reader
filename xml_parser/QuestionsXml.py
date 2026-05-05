from Dtos import (PreguntaEnsayoDto, PreguntaEmparejamientoDto, PreguntaOpcionMultipleDto, PreguntaVerdaderoFalsoDto)
import textwrap

class QuestionXml:

    @staticmethod
    def preguntaOpcionMultiple(pregunta: PreguntaOpcionMultipleDto, cantidadCorrectas: int):
        puntaje = QuestionXml.calcularPuntaje(cantidadCorrectas)
        bloquePregunta = ""
        bloquePregunta += (f""" 
<question type="multichoice">
    <name>
        <text>{pregunta.nombre_pregunta}</text>
    </name>
    <questiontext format="html">
        <text>
            <![CDATA[ <p>{pregunta.preg}</p> ]]>
        </text>
    </questiontext>
    <generalfeedback format="html">
        <text/>
    </generalfeedback>
    <defaultgrade>1.0000000</defaultgrade>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <idnumber/>
    <single>{"true" if puntaje == "100" else "false"}</single>
    <shuffleanswers>true</shuffleanswers>
    <answernumbering>abc</answernumbering>
    <showstandardinstruction>0</showstandardinstruction>
    <correctfeedback format="html">
    <text>
        <![CDATA[ <p>Respuesta correcta</p> ]]>
    </text>
    </correctfeedback>
    <partiallycorrectfeedback format="html">
        <text>
            <![CDATA[ <p>Respuesta parcialmente correcta.</p> ]]>
        </text>
    </partiallycorrectfeedback>
    <incorrectfeedback format="html">
        <text>
            <![CDATA[ <p>Respuesta incorrecta.</p> ]]>
        </text>
    </incorrectfeedback>
    <shownumcorrect/>
            """).strip()  + "\n"
        for respuesta in pregunta.respuestas.respuestas.values():
            bloque = ""
            bloque += textwrap.dedent(f"""
    <answer fraction="{QuestionXml.asignarPuntaje(puntaje, respuesta.ok)}" format="html">
        <text>
            <![CDATA[ <p>{respuesta.txt}</p> ]]>
        </text>
        <feedback format="html">
            <text>
                <![CDATA[ <p>{respuesta.retro}</p> ]]>
            </text>
        </feedback>
    </answer>
            """).strip()
            bloquePregunta += "\t" + bloque.replace("\n", "\n\t") + "\n"
        bloquePregunta += "</question>\n"
        return bloquePregunta
            

    
    @staticmethod
    def preguntaEnsayo(pregunta: PreguntaEnsayoDto):
        return
    
    @staticmethod
    def prguntaEmparejamiento(pregunta: PreguntaEmparejamientoDto):
        bloquePregunta = ""
        bloquePregunta += (f"""
<question type="matching">
    <name>
        <text>{pregunta.nombre_pregunta}</text>
    </name>
    <questiontext format="html">
        <text>
            <![CDATA[ <p>{pregunta.preg}</p> ]]>
        </text>
    </questiontext>
    <generalfeedback format="html">
        <text/>
    </generalfeedback>
    <defaultgrade>1.0000000</defaultgrade>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <idnumber/>
    <shuffleanswers>true</shuffleanswers>
    <correctfeedback format="html">
        <text>
            <![CDATA[ <p>Respuesta correcta</p> ]]>
        </text>
    </correctfeedback>
    <partiallycorrectfeedback format="html">
        <text>
            <![CDATA[ <p>Respuesta parcialmente correcta.</p> ]]>
        </text>
    </partiallycorrectfeedback>
    <incorrectfeedback format="html">
        <text>
            <![CDATA[ <p>Respuesta incorrecta.</p> ]]>
        </text>
    </incorrectfeedback>
    <shownumcorrect/>
        """)

        for respuesta in pregunta.respuestas.respuestas.values():
            bloque = ""
            bloque += textwrap.dedent(f"""
    <subquestion format="html">
        <text>
            <![CDATA[ <p>{respuesta.tabla.get("c0")}</p> ]]>
        </text>
        <answer>
            <text>{respuesta.tabla.get("c1")}</text>
        </answer>
    </subquestion>
            """).strip()
            bloquePregunta += "\t" + bloque.replace("\n", "\n\t") + "\n"

        bloquePregunta += "</question>\n"

        return bloquePregunta
    
    @staticmethod
    def preguntaVerdaderoFalso(pregunta: PreguntaVerdaderoFalsoDto):
        return
    
    @staticmethod
    def calcularPuntaje(cantidadCorrectas: int) -> str:
        return str((1/cantidadCorrectas)*100)
    
    @staticmethod
    def asignarPuntaje(puntaje: str, esCorrecta: bool):
        return puntaje if esCorrecta == True else '0'
    

        