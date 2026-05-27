import requests
import time
import os
from dotenv import load_dotenv
import sqlglot 
from sqlglot import expressions as exp
import re

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_MODEL = "gpt-4o-mini"


INTENCIONES = [
    "horarios",
    "contacto",
    "requisitos",
    "tramite",
    "baja_general",
    "baja_ingles",
    "servicio_social",
    "desarrollo_humano",
    "ingles",
    "biblioteca",
    "avisos",
    "calendario",
    "tutorias",
    "faq_general",
    "sin_contexto"
]
CLASIFICADOR_PROMPT = """
Eres un clasificador de intenciones para un chatbot universitario.

Clasifica el mensaje del usuario en UNA SOLA categoría.

Categorías válidas:
- horarios
- contacto
- requisitos
- tramite
- baja_general
- baja_ingles
- servicio_social
- desarrollo_humano
- ingles
- biblioteca
- avisos
- calendario
- tutorias
- faq_general
- sin_contexto

Reglas:

Si habla de problemas psicológicos, emocionales, personales, ansiedad, depresión, problemas en casa, apoyo, ayuda, asesoría, tutorías o psicólogo:
=> tutorias

Si habla de quitar inglés, baja de inglés, eliminar inglés, dar de baja inglés, ya no quiero inglés:
=> baja_ingles

Si habla de darme de baja, salirme de la carrera, dejar la universidad, baja académica, baja de carrera, abandonar carrera y NO menciona inglés:
=> baja_general

Si pregunta qué necesito, requisitos, documentos, papeles, qué piden, qué ocupo, qué llevo:
=> requisitos

Si pregunta cómo solicitar, cómo tramitar, cómo sacar, cómo obtener, proceso, pasos, qué tengo que hacer y menciona constancia, credencial, certificado, estacionamiento, ficha escolar, traslado, cambio de carrera o vigencia de derechos:
=> tramite

Si pregunta horario, abre, abren, cierra, cierran, a qué hora, atienden, atención:
=> horarios

Si pregunta teléfono, número, correo, email o contacto:
=> contacto

Si habla deregistrar mi servicio social, dar de alta el servicio social, servicio social, horas de servicio, reportes de servicio, formatos, dónde hacer servicio o cuándo empiezo servicio:
=> servicio_social

Si habla de puntos, DH, desarrollo humano, actividades culturales o eventos culturales:
=> desarrollo_humano

Si habla de inglés, certificación, examen de inglés, examen de ubicación, adelantar inglés, nivel de inglés o idioma:
=> ingles

Si habla de biblioteca, préstamo de libros, multa, pagar multa, días hábiles, devolver libro:
=> biblioteca

Si pregunta fechas, cuándo, calendario, evaluaciones, verano, vacaciones, cuándo empieza, cuándo termina, periodo:
=> calendario

Si pregunta avisos, anuncios, noticias, comunicados o información reciente:
=> avisos

Si habla de programa dual, modalidad dual, visitas industriales, reportar maestro, materia atrasada, abrir materia, justificantes o coordinación:
=> faq_general

Si no se puede clasificar:
=> sin_contexto

Responde SOLO con el nombre exacto de la categoría.
No expliques nada.
No uses markdown.
"""

def clasificar_intencion(texto: str):
    texto_lower = texto.lower()

    # 1. PRIORIDAD: problemas académicos/personales/emocionales
    palabras_tutorias = [
        "atorado",
        "atorada",
        "estresado",
        "estresada",
        "ansiedad",
        "depresion",
        "depresión",
        "triste",
        "reprobe",
        "reprobé",
        "me reprobo",
        "me reprobó",
        "no puedo",
        "me siento mal",
        "problemas",
        "ayuda",
        "apoyo",
        "asesoria",
        "asesoría",
        "psicologo",
        "psicólogo",
        "rendirme"
    ]

    if any(palabra in texto_lower for palabra in palabras_tutorias):
        return "tutorias"

    # 2. BAJA DE INGLÉS
    if (
        ("ingles" in texto_lower or "inglés" in texto_lower)
        and any(palabra in texto_lower for palabra in [
            "baja",
            "dar de baja",
            "quitar",
            "eliminar",
            "ya no quiero"
        ])
    ):
        return "baja_ingles"

    # 3. BAJA GENERAL
    if any(palabra in texto_lower for palabra in [
        "darme de baja",
        "dar de baja la carrera",
        "baja de carrera",
        "baja academica",
        "baja académica",
        "salirme de la carrera",
        "salirme de la universidad",
        "dejar la carrera",
        "abandonar carrera"
    ]):
        return "baja_general"
    # 4. TRÁMITE ESTACIONAMIENTO
    palabras_estacionamiento = [
        "carro",
        "coche",
        "auto",
        "vehiculo",
        "vehículo",
        "estacionamiento",
        "permiso",
        "placas"
    ]

    if any(p in texto_lower for p in palabras_estacionamiento):
        return "tramite"
    
        # 5. SERVICIO SOCIAL
    palabras_servicio_social = [
        "servicio social",
        "registrar servicio",
        "registrar mi servicio",
        "dar de alta servicio",
        "dar de alta mi servicio",
        "alta servicio",
        "liberar servicio",
        "horas de servicio",
        "reportes de servicio",
        "formatos de servicio",
        "donde hacer servicio",
        "dónde hacer servicio",
        "cuando empiezo servicio",
        "cuándo empiezo servicio"
    ]

    if any(p in texto_lower for p in palabras_servicio_social):
        return "servicio_social"

    # 4. IA como respaldo
    messages = [
        {"role": "system", "content": CLASIFICADOR_PROMPT},
        {"role": "user", "content": texto}
    ]

    respuesta, _ = _llamar_groq(
        messages,
        temperature=0,
        max_tokens=20
    )

    respuesta = respuesta.strip().lower()

    for categoria in INTENCIONES:
        if categoria in respuesta:
            return categoria

    return "sin_contexto"

PROMPT_TRAMITE = """
Genera únicamente SQL SELECT válido para MySQL.

Tablas:

Tramites(
    id_tramites,
    tipo,
    id_departamento
)

Requisito(
    id_tramite,
    descripcion,
    obligatorio
)

Relación:
Requisito.id_tramite = Tramites.id_tramites

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

SINÓNIMOS IMPORTANTES:

- carro
- coche
- auto
- vehículo
- permiso para carro
- permiso vehicular

=> corresponden a:
'Acceso al estacionamiento'

REGLAS:
- Solo SELECT
- Usa LIKE '%valor%'
- No expliques nada
- Responde solo SQL

Ejemplo:

SELECT t.tipo, r.descripcion, r.obligatorio
FROM Tramites t
JOIN Requisito r
ON r.id_tramite = t.id_tramites
WHERE t.tipo LIKE '%estacionamiento%';
"""
PROMPT_FAQ_GENERAL = """
Genera únicamente SQL SELECT válido para MySQL.

Tabla:
PreguntasFrecuentes(
    pregunta,
    respuesta,
    palabrasClave,
    categoria
)

Reglas:
- Solo SELECT
- Usa LIKE '%valor%'
- Busca en pregunta, respuesta y palabrasClave
- No expliques nada
- Responde solo SQL
- Si el usuario menciona programa dual o modalidad dual, busca 'dual'
- Si menciona reportar maestro, busca 'maestro' o 'reportar'
- Si menciona materia atrasada, busca 'materia' o 'atrasada'
- Si menciona visitas industriales, busca 'visita' o 'industrial'
- Si menciona justificante, busca 'justificante'

Ejemplo:

SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE pregunta LIKE '%dual%'
   OR respuesta LIKE '%dual%'
   OR palabrasClave LIKE '%dual%';
"""
PROMPT_HORARIOS = """
Genera únicamente una consulta SQL SELECT válida para MySQL.

Tabla:
Departamento(
    nombre,
    horaLlegada,
    horaSalida,
    descripcionHorario
)

Reglas:
- Solo SELECT
- Usa LIKE
- No expliques nada
- Responde solo SQL

Ejemplo:

Usuario: ¿A qué hora abre biblioteca?
SQL:
SELECT nombre, horaLlegada, horaSalida, descripcionHorario
FROM Departamento
WHERE nombre LIKE '%Biblioteca%';
"""

PROMPT_BAJA_INGLES = """
Genera únicamente SQL SELECT válido.

Tabla:
PreguntasFrecuentes(
    pregunta,
    respuesta,
    palabrasClave,
    categoria
)

La categoría correcta es 'Inglés'.

Usa LIKE para:
- baja
- quitar
- eliminar

Ejemplo:

SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE categoria = 'Inglés'
AND (
    pregunta LIKE '%baja%'
    OR respuesta LIKE '%baja%'
    OR palabrasClave LIKE '%quitar%'
);
"""
PROMPT_CONTACTO = """
Genera únicamente SQL SELECT válido para MySQL.

Tabla:
Departamento(
    nombre,
    correo,
    telefono
)

Reglas:
- Solo SELECT
- Usa LIKE '%valor%'
- No expliques nada
- Responde solo SQL

Ejemplo:

SELECT nombre, correo, telefono
FROM Departamento
WHERE nombre LIKE '%Control Escolar%';
"""
PROMPT_REQUISITOS = """
Genera únicamente SQL SELECT válido para MySQL.

Tablas:

Tramites(
    tipo,
    id_departamento
)

Requisito(
    id_tramite,
    descripcion,
    obligatorio
)

Relación:
Requisito.id_tramite = Tramites.id_tramites


Reglas:
- Solo SELECT
- Usa LIKE '%valor%'
- No expliques nada
- Responde solo SQL

Ejemplo:

SELECT t.tipo, r.descripcion, r.obligatorio
FROM Tramites t
JOIN Requisito r
ON r.id_tramite = t.id_tramites
WHERE t.tipo LIKE '%Credencial%';
"""
PROMPT_BAJA_GENERAL = """
Genera únicamente SQL SELECT válido para MySQL.

Tablas:

Tramites(
    tipo,
    id_departamento
)

Requisito(
    id_tramite,
    descripcion,
    obligatorio
)

Relación:
Requisito.id_tramite = Tramites.id_tramites

La baja existe como:
'Solicitud de baja'

Reglas:
- Solo SELECT
- No expliques nada
- Responde solo SQL

Ejemplo:

SELECT t.tipo, r.descripcion, r.obligatorio
FROM Tramites t
JOIN Requisito r
ON r.id_tramite = t.id_tramites
WHERE t.tipo LIKE '%baja%';
"""
PROMPT_SERVICIO_SOCIAL = """
Genera únicamente SQL SELECT válido para MySQL.

Tabla:
PreguntasFrecuentes(
    pregunta,
    respuesta,
    palabrasClave,
    categoria
)

La categoría correcta es:
'Servicio Social'

SINÓNIMOS:
- registrar servicio social
- dar de alta servicio social
- alta de servicio social
- liberar servicio social
- formatos
- reportes
- horas
- dónde hacerlo
- cuándo empiezo

Reglas:
- Solo SELECT
- Busca siempre dentro de categoria = 'Servicio Social'
- Usa LIKE en pregunta, respuesta y palabrasClave
- No expliques nada
- Responde solo SQL

Ejemplo:

SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE categoria = 'Servicio Social'
AND (
    pregunta LIKE '%servicio social%'
    OR respuesta LIKE '%servicio social%'
    OR palabrasClave LIKE '%servicio social%'
    OR pregunta LIKE '%formatos%'
    OR palabrasClave LIKE '%formatos%'
    OR pregunta LIKE '%horas%'
    OR palabrasClave LIKE '%horas%'
    OR pregunta LIKE '%reportes%'
    OR palabrasClave LIKE '%reportes%'
);
"""
PROMPT_DESARROLLO_HUMANO = """
Genera únicamente SQL SELECT válido para MySQL.

Tabla:
PreguntasFrecuentes(
    pregunta,
    respuesta,
    palabrasClave,
    categoria
)

La categoría correcta es:
'Desarrollo Humano'

Reglas:
- Solo SELECT
- Usa LIKE '%valor%'
- No expliques nada
- Responde solo SQL

Ejemplo:

SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE categoria = 'Desarrollo Humano'
AND (
    pregunta LIKE '%puntos%'
    OR respuesta LIKE '%puntos%'
    OR palabrasClave LIKE '%puntos%'
);
"""
PROMPT_INGLES = """
Genera únicamente SQL SELECT válido para MySQL.

Tabla:
PreguntasFrecuentes(
    pregunta,
    respuesta,
    palabrasClave,
    categoria
)

La categoría correcta es:
'Inglés'

Reglas:
- Solo SELECT
- Usa LIKE '%valor%'
- No expliques nada
- Responde solo SQL

Ejemplo:

SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE categoria = 'Inglés'
AND (
    pregunta LIKE '%certificación%'
    OR respuesta LIKE '%certificación%'
    OR palabrasClave LIKE '%certificación%'
);
"""
PROMPT_BIBLIOTECA = """
Genera únicamente SQL SELECT válido para MySQL.

Tabla:
PreguntasFrecuentes(
    pregunta,
    respuesta,
    palabrasClave,
    categoria
)

La categoría correcta es:
'Biblioteca'

Reglas:
- Solo SELECT
- Usa LIKE '%valor%'
- No expliques nada
- Responde solo SQL

Ejemplo:

SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE categoria = 'Biblioteca'
AND (
    pregunta LIKE '%multa%'
    OR respuesta LIKE '%multa%'
    OR palabrasClave LIKE '%multa%'
);
"""
PROMPT_TUTORIAS = """
Genera únicamente SQL SELECT válido para MySQL.

Tabla:
PreguntasFrecuentes(
    pregunta,
    respuesta,
    palabrasClave,
    categoria
)

La categoría correcta es:
'Tutorías'

Reglas:
- Solo SELECT
- Usa LIKE '%valor%'
- No expliques nada
- Responde solo SQL

Ejemplo:

SELECT pregunta, respuesta
FROM PreguntasFrecuentes
WHERE categoria = 'Tutorías'
AND (
    pregunta LIKE '%psicólogo%'
    OR respuesta LIKE '%psicólogo%'
    OR palabrasClave LIKE '%psicólogo%'
);
"""
PROMPT_CALENDARIO = """
Genera únicamente SQL SELECT válido para MySQL.

Tabla:
CalendarioEscolar(
    titulo,
    descripcion,
    fecha_inicio,
    fecha_fin,
    tipo
)

Reglas:
- Solo SELECT
- Usa LIKE '%valor%'
- No expliques nada
- Responde solo SQL

Ejemplo:

SELECT titulo, descripcion, fecha_inicio, fecha_fin, tipo
FROM CalendarioEscolar
WHERE titulo LIKE '%verano%'
OR descripcion LIKE '%verano%'
OR tipo LIKE '%verano%';
"""
PROMPT_AVISOS = """
Genera únicamente SQL SELECT válido para MySQL.

Tabla:
Avisos(
    titulo,
    contenido,
    fecha_inicio,
    fecha_fin
)

Reglas:
- Solo SELECT
- No expliques nada
- Responde solo SQL

Ejemplo:

SELECT titulo, contenido, fecha_inicio, fecha_fin
FROM Avisos
WHERE CURDATE() BETWEEN fecha_inicio AND fecha_fin;
"""
PROMPTS_SQL = {
    "horarios": PROMPT_HORARIOS,
    "contacto": PROMPT_CONTACTO,
    "requisitos": PROMPT_REQUISITOS,
    "tramite": PROMPT_TRAMITE,
    "baja_general": PROMPT_BAJA_GENERAL,
    "baja_ingles": PROMPT_BAJA_INGLES,
    "servicio_social": PROMPT_SERVICIO_SOCIAL,
    "desarrollo_humano": PROMPT_DESARROLLO_HUMANO,
    "ingles": PROMPT_INGLES,
    "biblioteca": PROMPT_BIBLIOTECA,
    "tutorias": PROMPT_TUTORIAS,
    "calendario": PROMPT_CALENDARIO,
    "avisos": PROMPT_AVISOS,
    "faq_general": PROMPT_FAQ_GENERAL,
}


def _llamar_groq(
    messages: list,
    temperature: float = 0.1,
    max_tokens: int = 500,
    mostrar_proveedor: bool = False
) -> tuple:
    """Retorna (texto, tokens_usados)"""

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
            data = response.json()
            respuesta = data["choices"][0]["message"]["content"].strip()
            tokens = data["usage"]["total_tokens"]  # ← Groq retorna esto

            if mostrar_proveedor:
                return "[Groq]\n" + respuesta, tokens

            return respuesta, tokens

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

    data = response.json()
    respuesta = data["choices"][0]["message"]["content"].strip()
    tokens = data["usage"]["total_tokens"]  # ← OpenAI también retorna esto

    if mostrar_proveedor:
        return "[ChatGPT]\n" + respuesta, tokens

    return respuesta, tokens


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
def validar_sql_select(sql: str):

    try:
        parsed = sqlglot.parse(sql)

        # Solo una consulta
        if len(parsed) != 1:
            return False

        query = parsed[0]

        # Debe ser SELECT
        if query.find(exp.Select) is None:
            return False

        sql_lower = sql.lower()

        palabras_prohibidas = [
            "insert",
            "update",
            "delete",
            "drop",
            "alter",
            "truncate",
            "grant",
            "revoke"
        ]

        if any(p in sql_lower for p in palabras_prohibidas):
            return False

        return True

    except Exception:
        return False


def generar_sql(texto: str):

    categoria = clasificar_intencion(texto)

    prompt = PROMPTS_SQL.get(categoria)

    if not prompt:
        return "SELECT 'No hay información disponible' AS respuesta;", 0

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": texto}
    ]

    sql, tokens = _llamar_groq(
        messages,
        temperature=0,
        max_tokens=150
    )

    sql = limpiar_sql(sql)

    if not validar_sql_select(sql):

        return "SELECT 'Consulta no válida' AS respuesta;", tokens

    return sql, tokens

    

def formatear_respuesta(pregunta: str, datos: list) -> tuple:
    messages = [
        {
            "role": "system",
           "content": """
Eres Chat Búho, un asistente amable y cercano de un instituto tecnológico.

Tu tarea es responder usando únicamente la información proporcionada en los datos de la base de datos, al tyerminar recuerda dar un dato curioso acerca de los buhos de forma amable, agrega stickers a la conversacion

Reglas:
- Sé natural y conversacional.
- Mantén un tono amable y humano.
- No inventes información.
- No des consejos fuera de la base de datos.
- No uses JSON.
- No uses markdown con negritas.
- No hagas párrafos gigantes.
- Si hay varios requisitos o pasos, usa viñetas con "•".
- Cada viñeta debe ir en una línea distinta.
- Puedes agregar una breve introducción o cierre amable.

Ejemplo:

Claro 😊

Para obtener el permiso de estacionamiento necesitas:

• Solicitar formato en Control Escolar.
• Copia ampliada al 200% de licencia de conducir.
• Copia ampliada al 200% de tarjeta de circulación.
• Copia ampliada al 200% de credencial de estudiante.

Si necesitas ayuda con otro trámite, aquí estoy. Por cierto sabias que
Los búhos no tienen globos oculares flotantes como nosotros; en realidad, sus ojos tienen forma de tubos alargados que están fijos en su cráneo gracias a unos huesos llamados anillos escleróticos. Como no pueden mover los ojos para mirar a los lados, la naturaleza los compensó con un cuello hiperflexible: ¡pueden girar la cabeza hasta 270 grados sin romperse un solo vaso sanguíneo ni cortar el flujo de sangre al cerebro!
"""
        },
        {
            "role": "user",
            "content": f"Pregunta del usuario: {pregunta}\n\nDatos:\n{datos}"
        }
    ]

    respuesta, tokens = _llamar_groq(
        messages,
        temperature=0.2,
        max_tokens=450
    )

    return respuesta.strip(), tokens
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

def es_pregunta_identidad(texto: str) -> bool:
    texto = texto.lower()

    frases = [
        "quien eres",
        "quién eres",
        "que eres",
        "qué eres",
        "que haces",
        "qué haces",
        "para que sirves",
        "para qué sirves",
        "que puedes hacer",
        "qué puedes hacer",
        "qué puedes hacer?",
        "quien es chatbuho",
        "quién es chatbuho"
    ]

    return any(f in texto for f in frases)