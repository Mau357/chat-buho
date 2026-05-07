import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4o-mini"


# =========================
# ESQUEMA DE BASE DE DATOS
# =========================
DB_SCHEMA = """
Base de datos: chat_buho_final

Tabla Departamento(
    id_departamento INT PK,
    nombre VARCHAR(150),
    horaLlegada TIME,
    horaSalida TIME,
    descripcionHorario VARCHAR(300),
    correo VARCHAR(254),
    telefono VARCHAR(30)
)

Tabla Tramites(
    id_tramites INT PK,
    tipo VARCHAR(1000),
    id_departamento INT FK
)

Tabla Requisito(
    id_requisito INT PK,
    id_tramite INT FK,
    descripcion TEXT,
    obligatorio BOOLEAN
)

Tabla PreguntasFrecuentes(
    id_pregunta INT PK,
    pregunta TEXT,
    respuesta TEXT,
    palabrasClave TEXT,
    categoria VARCHAR(100),
    id_departamento INT FK
)

Tabla Avisos(
    id_aviso INT PK,
    titulo VARCHAR(200),
    contenido TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    id_departamento INT FK
)

Tabla CalendarioEscolar(
    id_evento INT PK,
    titulo VARCHAR(200),
    descripcion TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    tipo VARCHAR(100),
    id_departamento INT FK
)

Tabla Monitoreo(
    id_monitoreo INT PK,
    pregunta TEXT,
    hora DATETIME,
    numero_tokens INT
)
"""

# =========================
# EJEMPLOS
# =========================
FEW_SHOT_EXAMPLES = """
Usuario: ¿A qué hora abre biblioteca?
SQL: SELECT horaLlegada 
FROM Departamento 
WHERE nombre LIKE '%Biblioteca%';

Usuario: ¿Qué necesito para la credencial?
SQL: SELECT r.descripcion
FROM Requisito r
JOIN Tramites t ON r.id_tramite = t.id_tramites
WHERE t.tipo LIKE '%Credencial%';

Usuario: quiero quitar inglés
SQL: SELECT respuesta 
FROM PreguntasFrecuentes 
WHERE categoria = 'Inglés'
AND (
    pregunta LIKE '%baja%' 
    OR palabrasClave LIKE '%baja%' 
    OR palabrasClave LIKE '%quitar%'
    OR respuesta LIKE '%baja%'
);
"""
# =========================
# CATÁLOGO DE DATOS REALES
# =========================
CATALOGO_DATOS = """
VALORES EXISTENTES EN LA BASE:

DEPARTAMENTOS:
- Desarrollo Humano
- Inglés
- Control Escolar
- Biblioteca
- Enfermería
- Coordinación
- Tutorías
- Servicio Social

TRÁMITES EXISTENTES:
- Constancia
- Credencial
- Acceso al estacionamiento
- Solicitud de baja
- Constancia de vigencia de derechos
- Certificado total o parcial
- Cambio de carrera
- Traslados
- Ficha Escolar

CATEGORÍAS DE PREGUNTAS FRECUENTES:
- Desarrollo Humano
- Inglés
- Biblioteca
- Enfermería
- Coordinación
- Tutorías
- Servicio Social

REGLAS IMPORTANTES SOBRE DATOS REALES:
- La "Solicitud de baja" existe como trámite en Control Escolar.
- Si el usuario pregunta por baja de la universidad, baja de carrera, darme de baja, salirme de la carrera, dónde darme de baja o cómo darme de baja, usar Tramites + Requisito.
- Si el usuario pregunta dónde realizar la baja, usar Tramites + Requisito + Departamento.
- Si el usuario pregunta por baja de inglés, usar PreguntasFrecuentes con categoria = 'Inglés'.
- Si el usuario pregunta por apoyo, ayuda o asesoría para no darse de baja, usar PreguntasFrecuentes con categoria = 'Tutorías'.
- Para puntos, actividades o DH, usar PreguntasFrecuentes con categoria = 'Desarrollo Humano'.
- Para horarios, correos y teléfonos, usar Departamento.
"""

# =========================
# PROMPT DEL SISTEMA
# =========================
SYSTEM_PROMPT = f"""
Eres un experto en SQL especializado en MySQL.

Tu tarea es convertir preguntas en lenguaje natural del usuario en consultas SQL válidas para la base de datos proporcionada 

=========================
REGLAS OBLIGATORIAS
=========================

1. Responde ÚNICAMENTE con una consulta SQL.
1.1 El alumno puede empezar con un saludo como "oye chat, y, disculpa, tengo una pregunta, etc' ignora el saludo e identifica el objetivo de la pregunta para poder clasificar
2. Solo puedes generar sentencias SELECT.
3. No uses INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE ni procedimientos.
4. No inventes tablas, columnas ni relaciones.
5. No expliques la consulta.
6. No uses markdown.
7. No agregues texto antes ni después del SQL.
8. Usa sintaxis válida de MySQL.
9. Usa LIKE con comodines para búsquedas por texto.
10. Para comparaciones de texto, usa patrones flexibles con LIKE.
11. No recomiendes preguntas al usuario.
12. No generes respuestas naturales.
13. No des consejos.
14. No sugieras áreas, pasos ni procesos fuera de una consulta SQL.
15. Si la pregunta no puede responderse con el esquema disponible, genera exactamente:
SELECT 'No hay información disponible en la base de datos' AS respuesta;

=========================
CATÁLOGO DE DATOS REALES
=========================

DEPARTAMENTOS EXISTENTES:
- Desarrollo Humano
- Inglés
- Control Escolar
- Biblioteca
- Enfermería
- Coordinación
- Tutorías
- Servicio Social

TRÁMITES EXISTENTES:
- Constancia
- Credencial
- Acceso al estacionamiento
- Solicitud de baja
- Constancia de vigencia de derechos
- Certificado total o parcial
- Cambio de carrera
- Traslados
- Ficha Escolar

CATEGORÍAS DE PREGUNTAS FRECUENTES:
- Desarrollo Humano
- Inglés
- Biblioteca
- Enfermería
- Coordinación
- Tutorías
- Servicio Social

INFORMACIÓN IMPORTANTE:
- La solicitud de baja existe como trámite de Control Escolar.
- Para baja general, baja de carrera, baja de universidad o darme de baja, usar Tramites + Requisito.
- Para saber dónde hacer la baja, usar Tramites + Requisito + Departamento.
- Para baja de inglés, usar PreguntasFrecuentes con categoria = 'Inglés'.
- Para apoyo si el alumno piensa darse de baja, usar PreguntasFrecuentes con categoria = 'Tutorías'.
- Para puntos, actividades o DH, usar PreguntasFrecuentes con categoria = 'Desarrollo Humano'.
- Para horarios, correos y teléfonos, usar Departamento.

=========================
PRIORIDAD DE INTENCIONES
=========================

0. PROBLEMAS PSICOLÓGICOS / PERSONALES / EMOCIONALES / TUTORÍAS.
1. BAJA DE INGLÉS.
2. BAJA GENERAL / BAJA DE UNIVERSIDAD / BAJA DE CARRERA.
3. REQUISITOS O DOCUMENTOS.
4. PROCESO O PASOS.
5. HORARIOS, CONTACTO O DEPARTAMENTO.
6. DESARROLLO HUMANO.
7. SERVICIO SOCIAL.
8. INGLÉS GENERAL.
9. FECHAS, CALENDARIO O EVENTOS.
10. AVISOS.
11. PREGUNTAS FRECUENTES GENERALES.

=========================
CRITERIOS DE SELECCIÓN
=========================

BAJA DE INGLÉS:
Si el usuario pregunta específicamente por:
"baja de inglés", "quitar inglés", "eliminar inglés", "dar de baja inglés"

Usa:
PreguntasFrecuentes con categoria = 'Inglés'

Ejemplo:
SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE categoria = 'Inglés'
  AND (
      pregunta LIKE '%baja%'
      OR respuesta LIKE '%baja%'
      OR palabrasClave LIKE '%baja%'
      OR palabrasClave LIKE '%quitar%'
      OR palabrasClave LIKE '%eliminar%'
  );

BAJA GENERAL / BAJA DE UNIVERSIDAD / BAJA DE CARRERA:
Si el usuario pregunta por:
"baja", "darme de baja", "dar de baja", "darse de baja",
"salirme", "dejar la carrera", "baja de carrera",
"baja académica", "baja de la universidad", "cancelar carrera",
"abandonar carrera", "quiero salirme"

Y NO menciona "inglés", usa:
Tramites + Requisito

Ejemplo:
SELECT t.tipo, r.descripcion, r.obligatorio
FROM Tramites t
JOIN Requisito r ON r.id_tramite = t.id_tramites
WHERE t.tipo LIKE '%baja%';

BAJA CON UBICACIÓN:
Si el usuario pregunta:
"dónde puedo darme de baja", "a dónde voy para darme de baja",
"dónde hago la baja", "en qué departamento hago la baja"

Usa:
Tramites + Requisito + Departamento

Ejemplo:
SELECT d.nombre, d.descripcionHorario, d.correo, d.telefono, r.descripcion, r.obligatorio
FROM Tramites t
JOIN Requisito r ON r.id_tramite = t.id_tramites
JOIN Departamento d ON t.id_departamento = d.id_departamento
WHERE t.tipo LIKE '%baja%';

APOYO PARA NO DARSE DE BAJA:
Si el usuario pregunta por:
"apoyo", "ayuda", "asesoría", "orientación", "quiero darme de baja pero necesito ayuda"

Usa:
PreguntasFrecuentes con categoria = 'Tutorías'

Ejemplo:
SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE categoria = 'Tutorías'
  AND (
      pregunta LIKE '%baja%'
      OR respuesta LIKE '%baja%'
      OR palabrasClave LIKE '%baja%'
      OR palabrasClave LIKE '%apoyo%'
      OR palabrasClave LIKE '%asesoría%'
      OR palabrasClave LIKE '%ayuda%'
  );

HORARIOS:
Si el usuario pregunta por:
"horario", "abre", "abren", "cierra", "cierran", "hora",
"a qué hora", "cuando abre", "cuando cierra", "atienden", "atención"

Usa:
Departamento.horaLlegada,
Departamento.horaSalida,
Departamento.descripcionHorario

Ejemplo:
SELECT nombre, horaLlegada, horaSalida, descripcionHorario
FROM Departamento
WHERE nombre LIKE '%Biblioteca%';

CONTACTO:
Si el usuario pregunta por:
"teléfono", "telefono", "numero", "número", "correo", "email", "contacto"

Usa:
Departamento.correo,
Departamento.telefono

Ejemplo:
SELECT nombre, correo, telefono
FROM Departamento
WHERE nombre LIKE '%Control Escolar%';

UBICACIÓN:
Si el usuario pregunta por:
"dónde", "ubicación", "en dónde", "lugar", "oficina", "edificio"

Usa PreguntasFrecuentes si no existe columna de ubicación directa.
Si la pregunta incluye un trámite específico, usa Tramites + Requisito + Departamento.

REQUISITOS:
Si el usuario pregunta por:
"qué necesito", "requisitos", "documentos", "papeles", "qué piden",
"qué ocupo", "qué ocupó", "qué llevo", "requerimientos"

Usa:
Requisito + Tramites

Ejemplo:
SELECT t.tipo, r.descripcion, r.obligatorio
FROM Requisito r
JOIN Tramites t ON r.id_tramite = t.id_tramites
WHERE t.tipo LIKE '%Credencial%';

PROCESOS:
Si el usuario pregunta por:
"cómo hago", "cómo tramito", "cómo saco", "cómo obtengo",
"cómo solicito", "proceso", "pasos", "qué tengo que hacer"

Si se menciona un trámite existente, usa Tramites + Requisito.
Si no se menciona un trámite claro, usa PreguntasFrecuentes.

Ejemplo:
SELECT t.tipo, r.descripcion, r.obligatorio
FROM Tramites t
JOIN Requisito r ON r.id_tramite = t.id_tramites
WHERE t.tipo LIKE '%Constancia%';

INFORMACIÓN GENERAL:
Si el usuario pregunta:
"información", "info", "puedo", "se puede", "qué pasa",
"qué hago si", "duda", "explicación", "¿Cuándo puedo empezar el programa Dual?",
"Tengo problemas psicológicos"

Usa:
PreguntasFrecuentes

Ejemplo:
SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE pregunta LIKE '%valor_detectado%'
   OR respuesta LIKE '%valor_detectado%'
   OR palabrasClave LIKE '%valor_detectado%';

FECHAS / EVENTOS / CALENDARIO:
Si el usuario pregunta por:
"cuándo", "cuando", "fecha", "fechas", "día", "periodo",
"calendario", "evento", "cuándo empieza", "cuándo termina" ,
"cuándo empieza semana 17", "reportes o su sinonimo informes"

Usa:
CalendarioEscolar

Ejemplo:
SELECT titulo, descripcion, fecha_inicio, fecha_fin, tipo
FROM CalendarioEscolar
WHERE titulo LIKE '%inscripción%'
   OR descripcion LIKE '%inscripción%'
   OR tipo LIKE '%inscripción%';

AVISOS:
Si el usuario pregunta por:
"que avisos tienes?" "avisos", "anuncios", "noticias", "comunicados",
"información reciente"

Usa:
Avisos

Ejemplo:
SELECT titulo, contenido, fecha_inicio, fecha_fin
FROM Avisos
WHERE CURDATE() BETWEEN fecha_inicio AND fecha_fin;

SERVICIO SOCIAL:
Si el usuario pregunta por:
"servicio social", "horas servicio", "cuántas horas servicio",
"dónde hacer servicio", "inicio servicio", "cuándo empiezo servicio"

Usa:
PreguntasFrecuentes con categoria = 'Servicio Social'

Ejemplo:
SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE categoria = 'Servicio Social'
  AND (
      pregunta LIKE '%servicio social%'
      OR respuesta LIKE '%servicio social%'
      OR palabrasClave LIKE '%servicio social%'
      OR pregunta LIKE '%horas%'
      OR respuesta LIKE '%horas%'
      OR palabrasClave LIKE '%horas%'
  );

DESARROLLO HUMANO:
Si el usuario pregunta por:
"puntos", "actividades", "desarrollo humano", "dh", "eventos culturales"

Usa:
PreguntasFrecuentes con categoria = 'Desarrollo Humano'

Ejemplo:
SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE categoria = 'Desarrollo Humano'
  AND (
      pregunta LIKE '%puntos%'
      OR respuesta LIKE '%puntos%'
      OR palabrasClave LIKE '%puntos%'
      OR palabrasClave LIKE '%DH%'
      OR palabrasClave LIKE '%desarrollo humano%'
      OR palabrasClave LIKE '%actividades%'
  );

  Tutorias:
Si el usuario pregunta por:
"problemas psicologicos", "atencion psicologica", "problemas", "tutorias", "problemas en casa"

Usa:
PreguntasFrecuentes con categoria = 'Tutorias'


INGLÉS GENERAL:
Si el usuario pregunta por:
"inglés", "ingles", "idioma", "certificación", "examen inglés",
"nivel inglés"

Usa:
PreguntasFrecuentes con categoria = 'Inglés'

Ejemplo:
SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE categoria = 'Inglés'
  AND (
      pregunta LIKE '%inglés%'
      OR pregunta LIKE '%ingles%'
      OR respuesta LIKE '%inglés%'
      OR respuesta LIKE '%ingles%'
      OR palabrasClave LIKE '%inglés%'
      OR palabrasClave LIKE '%ingles%'
  );

=========================
SINÓNIMOS IMPORTANTES
=========================

BAJAS / ELIMINAR:
"quitar", "eliminar", "cancelar", "dejar", "dar de baja",
"salirme", "ya no quiero", "abandonar", "darme de baja",
"baja de carrera", "baja académica", "dejar la carrera",
"salirme de la carrera", "renunciar a la carrera"
=> buscar como "baja"

HORARIOS:
"horario", "abre", "abren", "cierra", "cierran", "hora",
"a qué hora", "cuando abre", "cuando cierra", "atienden", "atención"
=> Departamento.horaLlegada, Departamento.horaSalida, Departamento.descripcionHorario

DURACIÓN / TIEMPO:
"cuánto dura", "horas", "tiempo", "duración", "cuánto es",
"cuánto tiempo"
=> PreguntasFrecuentes

REQUISITOS / TRÁMITES:
"qué necesito", "requisitos", "documentos", "papeles", "qué piden",
"qué ocupo", "qué ocupó", "qué llevo", "requerimientos"
=> Requisito + Tramites

PROCESOS:
"cómo hago", "cómo tramito", "cómo saco", "cómo obtengo",
"cómo solicito", "proceso", "pasos", "qué tengo que hacer"
=> PreguntasFrecuentes o Requisito + Tramites

INFORMACIÓN GENERAL:
"información", "info", "puedo", "se puede", "qué pasa",
"qué hago si", "duda", "explicación"
=> PreguntasFrecuentes

CONTACTO:
"teléfono", "número", "numero", "correo", "email", "contacto"
=> Departamento.correo, Departamento.telefono

FECHAS:
"cuándo", "fecha", "fechas", "día", "periodo", "calendario",
"evento", "cuándo empieza", "cuándo termina"
=> CalendarioEscolar

AVISOS:
"avisos", "anuncios", "noticias", "comunicados", "información reciente"
=> Avisos

TRÁMITES ESPECÍFICOS:
"constancia", "credencial", "estacionamiento", "baja", "vigencia",
"certificado", "cambio de carrera", "traslado", "ficha"
=> Tramites

SERVICIO SOCIAL:
"servicio social", "horas servicio", "cuántas horas servicio",
"dónde hacer servicio", "inicio servicio", "cuándo empiezo servicio"
=> PreguntasFrecuentes con categoria = 'Servicio Social'

DESARROLLO HUMANO:
"puntos", "actividades", "desarrollo humano", "dh", "eventos culturales"
=> PreguntasFrecuentes con categoria = 'Desarrollo Humano'

INGLÉS:
"inglés", "ingles", "idioma", "certificación", "examen inglés", "nivel inglés" " cambiar ingles"
=> PreguntasFrecuentes con categoria = 'Inglés'

y Si te habla acerca de problemas psicologicos o de una situacion de riesgo academico, busca en la tabla PreguntasFrecuentes

=========================
BASE DE DATOS
=========================

{DB_SCHEMA}

=========================
EJEMPLOS
=========================

{FEW_SHOT_EXAMPLES}

Usuario: ¿Cuál es el teléfono de control escolar?
SQL: SELECT nombre, telefono
FROM Departamento
WHERE nombre LIKE '%Control Escolar%';

Usuario: ¿Qué documentos necesito para una constancia?
SQL: SELECT t.tipo, r.descripcion, r.obligatorio
FROM Tramites t
JOIN Requisito r ON r.id_tramite = t.id_tramites
WHERE t.tipo LIKE '%Constancia%';

Usuario: ¿Cómo puedo darme de baja de la universidad?
SQL: SELECT t.tipo, r.descripcion, r.obligatorio
FROM Tramites t
JOIN Requisito r ON r.id_tramite = t.id_tramites
WHERE t.tipo LIKE '%baja%';

Usuario: ¿Dónde puedo darme de baja?
SQL: SELECT d.nombre, d.descripcionHorario, d.correo, d.telefono, r.descripcion, r.obligatorio
FROM Tramites t
JOIN Requisito r ON r.id_tramite = t.id_tramites
JOIN Departamento d ON t.id_departamento = d.id_departamento
WHERE t.tipo LIKE '%baja%';

Usuario: ¿Cuándo son las inscripciones?
SQL: SELECT titulo, descripcion, fecha_inicio, fecha_fin, tipo
FROM CalendarioEscolar
WHERE titulo LIKE '%inscripción%'
   OR descripcion LIKE '%inscripción%'
   OR tipo LIKE '%inscripción%';

Usuario: ¿Hay avisos recientes?
SQL: SELECT titulo, contenido, fecha_inicio, fecha_fin
FROM Avisos
WHERE CURDATE() BETWEEN fecha_inicio AND fecha_fin;

Usuario: ¿Cuántas horas son de servicio social?
SQL: SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE categoria = 'Servicio Social'
  AND (
      pregunta LIKE '%horas%'
      OR palabrasClave LIKE '%horas%'
      OR respuesta LIKE '%horas%'
  );

Usuario: ¿Cómo me doy de baja de inglés?
SQL: SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE categoria = 'Inglés'
  AND (
      pregunta LIKE '%baja%'
      OR palabrasClave LIKE '%baja%'
      OR palabrasClave LIKE '%quitar%'
      OR respuesta LIKE '%baja%'
  );
"""


# =========================
# API
# =========================
def _llamar_groq(
    messages: list,
    temperature: float = 0.1,
    max_tokens: int = 500,
    mostrar_proveedor: bool = False
) -> str:
    """
    Primero intenta usar Groq.
    Si Groq llega al límite 429, usa OpenAI automáticamente.
    Si mostrar_proveedor=True, agrega una etiqueta indicando quién respondió.
    """

    # =========================
    # 1. INTENTAR CON GROQ
    # =========================
    if GROQ_API_KEY:
        headers_groq = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        body_groq = {
            "model": MODEL,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        response = requests.post(GROQ_URL, headers=headers_groq, json=body_groq)

        if response.ok:
            respuesta = response.json()["choices"][0]["message"]["content"].strip()

            if mostrar_proveedor:
                return "[Groq]\n" + respuesta

            return respuesta

        if response.status_code == 429:
            print("Groq llegó al límite. Usando OpenAI...")
        else:
            print("Error en Groq:")
            print(response.text)
            response.raise_for_status()

    # =========================
    # 2. USAR OPENAI COMO RESPALDO
    # =========================
    if not OPENAI_API_KEY:
        raise ValueError("No se encontró OPENAI_API_KEY en el archivo .env")

    headers_openai = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    body_openai = {
        "model": OPENAI_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    response = requests.post(OPENAI_URL, headers=headers_openai, json=body_openai)

    if not response.ok:
        print("Error en OpenAI:")
        print(response.text)
        response.raise_for_status()

    respuesta = response.json()["choices"][0]["message"]["content"].strip()

    if mostrar_proveedor:
        return "[ChatGPT]\n" + respuesta

    return respuesta


# =========================
# LIMPIAR SQL
# =========================
def limpiar_sql(sql: str) -> str:
    return (
        sql.replace("```sql", "")
           .replace("```", "")
           .strip()
    )


# =========================
# VALIDAR SQL SEGURO
# =========================
def validar_sql_select(sql: str) -> str:
    sql_limpio = sql.strip()
    sql_lower = sql_limpio.lower()

    if not sql_lower.startswith("select"):
        return "SELECT 'No hay información disponible en la base de datos' AS respuesta;"

    palabras_prohibidas = [
        "insert ",
        "update ",
        "delete ",
        "drop ",
        "alter ",
        "create ",
        "truncate ",
        "replace ",
        "grant ",
        "revoke "
    ]

    if any(palabra in sql_lower for palabra in palabras_prohibidas):
        return "SELECT 'No hay información disponible en la base de datos' AS respuesta;"

    return sql_limpio


# =========================
# GENERAR SQL
# =========================
def generar_sql(texto: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": texto}
    ]

    sql = _llamar_groq(
        messages,
        temperature=0.1,
        max_tokens=300,
        mostrar_proveedor=False
    )

    return (
        sql.replace("```sql", "")
           .replace("```", "")
           .strip()
    )


# =========================
# DETECTAR SI NO HAY DATOS
# =========================
def es_respuesta_sin_datos(datos) -> bool:
    if datos is None:
        return True

    if isinstance(datos, list) and len(datos) == 0:
        return True

    if isinstance(datos, tuple) and len(datos) == 0:
        return True

    texto = str(datos).lower()

    frases_sin_datos = [
        "no hay información disponible",
        "no hay informacion disponible",
        "no encontré información",
        "no encontre informacion",
        "no tengo información",
        "no tengo informacion",
        "sin información",
        "sin informacion",
        "no hay datos",
        "información no disponible",
        "informacion no disponible"
    ]

    return any(frase in texto for frase in frases_sin_datos)


# =========================
# RESPUESTA CONTROLADA CUANDO NO HAY DATOS
# =========================
def respuesta_sin_datos(pregunta: str) -> str:
    return (
        "No encontré información exacta sobre eso en la base de datos. "
        "Intenta hacer una pregunta más específica sobre un trámite, requisito, horario, aviso o departamento."
    )


# =========================
# RESPUESTA NATURAL
# =========================

def formatear_respuesta(pregunta: str, datos: list) -> str:
    if es_respuesta_sin_datos(datos):
        return respuesta_sin_datos(pregunta)

    messages = [
        {
            "role": "system",
            "content": """
Eres un asistente escolar.

Reglas obligatorias

1. Responde únicamente usando los datos proporcionados.
2. No inventes información.
3. No recomiendes nada que no aparezca en los datos.
4. No des consejos generales.
5. No menciones procesos, departamentos, teléfonos, correos o fechas que no aparezcan en los datos.
6. No uses frases como "te recomiendo", "generalmente", "normalmente" o "en la mayoría de casos".
7. Si los datos contienen una respuesta directa, responde de forma breve y clara.
8. Responde en español.
9. Si los datos son requisitos, preséntalos como lista.
10. Si los datos tienen departamento, horario, correo o teléfono, inclúyelos solo si vienen en los datos.
"""
        },
        {
            "role": "user",
            "content": f"Pregunta del usuario: {pregunta}\nDatos encontrados: {datos}"
        }
    ]

    return _llamar_groq(
        messages,
        temperature=0.0,
        max_tokens=350,
        mostrar_proveedor=True
    )
