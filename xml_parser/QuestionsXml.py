from Dtos import (PreguntaEnsayoDto, PreguntaEmparejamientoDto,
                  PreguntaOpcionMultipleDto, PreguntaVerdaderoFalsoDto,
                  OpcionDeRespuestaEnsayoDto, OpcionDeRespuestaDto)
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
        respuestas = [QuestionXml.respuestasEnsayo(bloqueRespuesta) for bloqueRespuesta in pregunta.respuestas.respuestas.values()][0]
        
        return (f"""
<question type="essay">
    <name>
        <text>{pregunta.nombre_pregunta}</text>
    </name>
    <questiontext format="html">
        <text>
            <![CDATA[ <p>{pregunta.preg}</p> ]]>
        </text>
    </questiontext>
    <generalfeedback format="html">
        <text>
            <![CDATA[ <p>{respuestas.get("txt")}</p> ]]>
        </text>
    </generalfeedback>
    <defaultgrade>1.0000000</defaultgrade>
    <penalty>0.0000000</penalty>
    <hidden>0</hidden>
    <idnumber/>
    <responseformat>editor</responseformat>
    <responserequired>1</responserequired>
    <responsefieldlines>10</responsefieldlines>
    <minwordlimit/>
    <maxwordlimit/>
    <attachments>0</attachments>
    <attachmentsrequired>0</attachmentsrequired>
    <maxbytes>0</maxbytes>
    <filetypeslist/>
    <graderinfo format="html">
        <text/>
    </graderinfo>
    <responsetemplate format="html">
        <text/>
    </responsetemplate>
</question>
        """) 
    
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
        bloquePregunta = ""
        respuestas = [QuestionXml.respuestasVerdaderoFalso(bloquePregunta) for bloquePregunta in pregunta.respuestas.respuestas.values()]

        bloquePregunta += (f"""
<question type="truefalse">
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
    <penalty>1.0000000</penalty>
    <hidden>0</hidden>
    <idnumber/>
""").strip()  + "\n"
        
        for respuesta in respuestas:
            bloque = ""
            bloque += textwrap.dedent(f"""
    <answer fraction="{QuestionXml.asignarPuntaje("100", respuesta.get("ok"))}" format="moodle_auto_format">
        <text>{"true" if respuesta.get("ok") else "false"}</text>
        <feedback format="html">
            <text>
                <![CDATA[ <p>{respuesta.get("retro")}</p> ]]>
            </text>
        </feedback>
    </answer>
    """).strip()
            bloquePregunta += "\t" + bloque.replace("\n", "\n\t") + "\n"

        bloquePregunta += "</question>\n"
        return bloquePregunta

    @staticmethod
    def calcularPuntaje(cantidadCorrectas: int) -> str:
        return str((1/cantidadCorrectas)*100)
    
    @staticmethod
    def asignarPuntaje(puntaje: str, esCorrecta) -> str:
        return puntaje if esCorrecta == True else '0'
    
    @staticmethod
    def respuestasVerdaderoFalso(respuesta: OpcionDeRespuestaDto):
        return {
            "txt": respuesta.txt,
            "retro": respuesta.retro,
            "ok": respuesta.ok,
            "img": respuesta.img or None
        }

    @staticmethod
    def respuestasEnsayo(respuesta: OpcionDeRespuestaEnsayoDto):
        return {
            "txt": respuesta.txt,
            "tabla": respuesta.tabla,
            "img": respuesta.img or None
        }
    

        