from Dtos import (PreguntaEnsayoDto, PreguntaEmparejamientoDto,
                  PreguntaOpcionMultipleDto, PreguntaVerdaderoFalsoDto,
                  OpcionDeRespuestaDto, CourseDataDto, OpcionDeRespuestaEnsayoDto)
import textwrap
import time

class MoodleXml:

    @staticmethod
    def preguntaOpcionMultiple(pregunta: PreguntaOpcionMultipleDto, cantidadCorrectas: int):
        puntaje = MoodleXml.calcularPuntaje(cantidadCorrectas)
        respuestas = [MoodleXml.respuestasDePregunta(bloquePregunta) for bloquePregunta in pregunta.respuestas.respuestas.values()]
        imagenes = ''
        bloquePregunta = "\t"
        bloquePregunta += (f"""
            <question type="multichoice">
                <name>
                    <text>{pregunta.nombre_pregunta}</text>
                </name>
                <questiontext format="html">
                    <text>
        """)
        if pregunta.img:
            nombreDeImagen = MoodleXml.crearNombreImg()
            imagen = pregunta.img.get("b64")
            formato = pregunta.img.get("fmt")
            bloquePregunta += f'<![CDATA[ <p>{pregunta.preg}</p> <p><img class="img-fluid" src="@@PLUGINFILE@@/{nombreDeImagen}.{formato}"></p> ]]>'
            imagenes += MoodleXml.crearBloqueImagen(nombreDeImagen, imagen, formato)
        else:
            bloquePregunta += f'<![CDATA[ <p>{pregunta.preg}</p> ]]>'

        bloquePregunta += '</text>\n'
        bloquePregunta += imagenes
        bloquePregunta += (f"""
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
        for respuesta in respuestas:
            respuesta = OpcionDeRespuestaDto(**respuesta)
            bloque = ""
            xmlContent = textwrap.dedent(f"""
                <answer fraction="{MoodleXml.asignarPuntaje(puntaje, respuesta.ok)}" format="html">
                    <text>
                        <![CDATA[ <p>{respuesta.txt}</p> ]]>
                    </text>
                    <feedback format="html">
                        <text>
                            <![CDATA[ <p>{respuesta.retro}</p> ]]>
                        </text>
                    </feedback>
            """).strip() + "\n"

            if respuesta.img is not None:
                nombreDeImagen = MoodleXml.crearNombreImg()
                imagen = respuesta.img.get("b64")
                formato = respuesta.img.get("fmt")
                xmlContent += MoodleXml.crearBloqueImagen(nombreDeImagen, imagen, formato)
            
            xmlContent += "</answer>\n"

            bloque += textwrap.indent(xmlContent, "\t")
            bloquePregunta += "\t" + bloque.replace("\n", "\n\t") + "\n"

        bloquePregunta += "\t</question>\n"
        return bloquePregunta

    @staticmethod
    def preguntaEnsayo(pregunta: PreguntaEnsayoDto):
        bloquePregunta = ""

        bloquePregunta += (f"""
            <question type="essay">
                <name>
                    <text>{pregunta.nombre_pregunta}</text>
                </name>
                <questiontext format="html">
                    <text>
        """)
        if pregunta.img:
            nombreDeImagen = MoodleXml.crearNombreImg()
            imagen = pregunta.img.get("b64")
            formato = pregunta.img.get("fmt")
            bloquePregunta += f'<![CDATA[ <p>{pregunta.preg}</p> <p><img class="img-fluid" src="@@PLUGINFILE@@/{nombreDeImagen}.{formato}"></p> ]]>'
            bloquePregunta += MoodleXml.crearBloqueImagen(nombreDeImagen, imagen, formato)
        else:
            bloquePregunta += f'<![CDATA[ <p>{pregunta.preg}</p> ]]>'
                           
        bloquePregunta += ("""</text>
                </questiontext>
                <generalfeedback format="html">
                    <text>
            """)
        
        cData = "<![CDATA[ "
        imagenes = ""
        
        for respuesta in pregunta.respuestas.respuestas.values():

            if respuesta.img is not None:

                nombreDeImagen = MoodleXml.crearNombreImg()
                imagen = respuesta.img.get("b64")
                formato = respuesta.img.get("fmt")
                
                cData += f'<p>{respuesta.txt}</p> <p><img class="img-fluid" src="@@PLUGINFILE@@/{nombreDeImagen}.{formato}"></p>'
                imagenes += MoodleXml.crearBloqueImagen(nombreDeImagen, imagen, formato)
            
            else:
                cData += f"<p>{respuesta.txt}</p>"
            
            
            if respuesta.tabla is not None:
                cData += f'<p>{respuesta.txt}</p> <table style="border-collapse: collapse; width: 100%;" border="1"><colgroup><col style="width: 33.3333%;"><col style="width: 33.3333%;"><col style="width: 33.3333%;"></colgroup> <tbody> '
                for fila in respuesta.tabla.values():
                    cData += '<tr> '

                    for columna in fila.values():

                        if isinstance(columna, dict):

                            texto = columna.get("txt", "")

                            cData += f'<td>{texto}'

                            if columna.get("img"):
                                nombreDeImagen = MoodleXml.crearNombreImg()
                                imagen = columna["img"].get("b64")
                                formato = columna["img"].get("fmt")

                                cData += f'<p><img class="img-fluid" src="@@PLUGINFILE@@/{nombreDeImagen}.{formato}"></p>'

                                imagenes += MoodleXml.crearBloqueImagen(nombreDeImagen, imagen, formato)

                            cData += '</td> '

                        else:
                            cData += f'<td>{columna}</td> '

                    cData += '</tr> '
                cData += '</tbody> </table>'

        cData += ' ]]>'
        bloquePregunta += cData + "\n</text>"
        bloquePregunta += imagenes + "\n"

        bloquePregunta += ("""
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
        """).strip() + "\n"
        return bloquePregunta
    
    @staticmethod
    def prguntaEmparejamiento(pregunta: PreguntaEmparejamientoDto):

        bloquePregunta = "\t"
        bloquePregunta += (f"""
            <question type="matching">
                <name>
                    <text>{pregunta.nombre_pregunta}</text>
                </name>
                <questiontext format="html">
                    <text>
        """)

        if pregunta.img:
            nombreDeImagen = MoodleXml.crearNombreImg()
            imagen = pregunta.img.get("b64")
            formato = pregunta.img.get("fmt")
            bloquePregunta += f'<![CDATA[ <p>{pregunta.preg}</p> <p><img class="img-fluid" src="@@PLUGINFILE@@/{nombreDeImagen}.{formato}"></p> ]]>'
            bloquePregunta += MoodleXml.crearBloqueImagen(nombreDeImagen, imagen, formato)
        else:
            bloquePregunta += f'<![CDATA[ <p>{pregunta.preg}</p> ]]>'
        
        bloquePregunta += ("""</text>
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
        """).strip() + "\n"

        for respuesta in pregunta.respuestas.respuestas.values():
            bloque = ""
            xmlContent = textwrap.dedent(f"""
                <subquestion format="html">
                    <text>
                        <![CDATA[ <p>{respuesta.get("c0")}</p> ]]>
                    </text>""").strip() + "\n"
            
            if respuesta.get("img") is not None:
                nombreDeImagen = MoodleXml.crearNombreImg()
                imagen = respuesta["img"].get("b64") # type: ignore[attr-defined]
                formato = respuesta["img"].get("fmt") # type: ignore[attr-defined]
                xmlContent += MoodleXml.crearBloqueImagen(nombreDeImagen, imagen, formato)

            xmlContent += textwrap.dedent(f"""
                <answer>
                    <text>{respuesta.get("c1")}</text>
                </answer>
            </subquestion>
            """).strip() + "\n"

            bloque += textwrap.indent(xmlContent, "\t")
            bloquePregunta += "\t" + bloque.replace("\n", "\n\t") + "\n"

        bloquePregunta += "</question>\n"

        return bloquePregunta
    
    @staticmethod
    def preguntaVerdaderoFalso(pregunta: PreguntaVerdaderoFalsoDto):
        respuestas = [MoodleXml.respuestasDePregunta(bloquePregunta) for bloquePregunta in pregunta.respuestas.respuestas.values()]
        bloquePregunta = "\t"

        bloquePregunta += (f"""
            <question type="truefalse">
                <name>
                    <text>{pregunta.nombre_pregunta}</text>
                </name>
                <questiontext format="html">
                    <text>
        """).strip() + "\n"

        if pregunta.img:
            nombreDeImagen = MoodleXml.crearNombreImg()
            imagen = pregunta.img.get("b64")
            formato = pregunta.img.get("fmt")
            bloquePregunta += f'<![CDATA[ <p>{pregunta.preg}</p> <p><img class="img-fluid" src="@@PLUGINFILE@@/{nombreDeImagen}.{formato}"></p> ]]>'
            bloquePregunta += MoodleXml.crearBloqueImagen(nombreDeImagen, imagen, formato)
        else:
            bloquePregunta += f'<![CDATA[ <p>{pregunta.preg}</p> ]]>'

        bloquePregunta += ("""
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
            respuesta = OpcionDeRespuestaDto(**respuesta)
            bloque = ""
            xmlContent = textwrap.dedent(f"""
                <answer fraction="{MoodleXml.asignarPuntaje("100", respuesta.ok)}" format="moodle_auto_format">
                    <text>{"true" if respuesta.ok else "false"}</text>
                    <feedback format="html">
                        <text>
                            <![CDATA[ <p>{respuesta.retro}</p> ]]>
                        </text>
            """).strip()

            if respuesta.img is not None:
                nombreDeImagen = MoodleXml.crearNombreImg()
                imagen = respuesta.img.get("b64")
                formato = respuesta.img.get("fmt")
                xmlContent += MoodleXml.crearBloqueImagen(nombreDeImagen, imagen, formato)
            
            xmlContent += ("""
                        </feedback>
                    </answer>\n""")
            
            bloque += textwrap.indent(xmlContent, "\t")
            bloquePregunta += "\t" + bloque.replace("\n", "\n\t") + "\n"

        bloquePregunta += "</question>\n"
        return bloquePregunta
    
    @staticmethod
    def crearNuevaCategoria(bloqueDeCategoria: CourseDataDto):
        bloque = "\t"
        xmlContent = textwrap.dedent(f"""
                <question type="category">
                    <category>
                        <text>$course$/top/{bloqueDeCategoria.courseLang}/{MoodleXml.tipoActividad(str(bloqueDeCategoria.courseActv))}</text>
                    </category>
                    <info format="html">
                        <text/>
                    </info>
                    <idnumber/>
                </question>
            """).strip()
        bloque = textwrap.indent(xmlContent, "\t")
        return bloque + "\n"


    @staticmethod
    def calcularPuntaje(cantidadCorrectas: int) -> str:
        return str((1/cantidadCorrectas)*100)
    
    @staticmethod
    def asignarPuntaje(puntaje: str, esCorrecta) -> str:
        return puntaje if esCorrecta else '0'
    
    @staticmethod
    def respuestasDePregunta(respuesta: OpcionDeRespuestaDto):
        return {
            "txt": respuesta.txt,
            "retro": respuesta.retro,
            "ok": respuesta.ok,
            "img": respuesta.img or None
        }
    
    @staticmethod
    def tipoActividad(actividad: str):
        if actividad == "CO":
            return "examen"
        elif actividad == "Test":
            return "auto"
        elif actividad == "Tarea":
            return "reflexion"
        elif actividad == "Rec01":
            return "recuperacion 1"
        elif actividad == "Rec02":
            return "recuperacion 2"
    
    @staticmethod
    def crearNombreImg():
        return str(time.time()).replace(".", str(ord(".")))
    
    @staticmethod
    def crearBloqueImagen(nombreDeImagen, imagen, formato):
        return (
            f'<file name="{nombreDeImagen}.{formato}" path="/"\n'
            f'encoding="base64">{imagen}\n'
            f'</file>'
        )
    

        