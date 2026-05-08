from fastapi import APIRouter
from pydantic import BaseModel

from ..services.groq_service import generar_sql, formatear_respuesta, es_respuesta_sin_datos, respuesta_sin_datos
from ..database.conection import ejecutar_query, guardar_sin_respuesta, guardar_monitoreo, calificar_respuesta

router = APIRouter()

class Mensaje(BaseModel):
    texto: str


class Calificacion(BaseModel):
    id_monitoreo: int
    util: int  # ← int en lugar de bool, valores del 1 al 5

@router.post("/chat")
def chat(mensaje: Mensaje):
    # 1. Generar SQL
    sql, tokens_sql = generar_sql(mensaje.texto)

    # 2. Ejecutar SQL
    try:
        datos = ejecutar_query(sql)
    except Exception as e:
        guardar_monitoreo(mensaje.texto, sql, str(e), 0, False)
        return {"respuesta": f"Error al consultar la base de datos: {str(e)}"}

    # 3. Sin datos
    if es_respuesta_sin_datos(datos):
        guardar_sin_respuesta(mensaje.texto)
        respuesta = respuesta_sin_datos(mensaje.texto)
        guardar_monitoreo(mensaje.texto, sql, respuesta, tokens_sql, False)
        return {"respuesta": respuesta, "id_monitoreo": None}

    # 4. Formatear respuesta
    try:
        respuesta_natural, tokens_respuesta = formatear_respuesta(mensaje.texto, datos)
    except Exception as e:
        guardar_monitoreo(mensaje.texto, sql, str(e), tokens_sql, False)
        return {"respuesta": f"Error al formatear respuesta: {str(e)}"}

    # 5. Guardar monitoreo y retornar id
    total_tokens = tokens_sql + tokens_respuesta
    id_monitoreo = guardar_monitoreo(mensaje.texto, sql, respuesta_natural, total_tokens, True)

    return {"respuesta": respuesta_natural, "id_monitoreo": id_monitoreo}


@router.put("/chat/calificar")
def calificar(calificacion: Calificacion):
    calificar_respuesta(calificacion.id_monitoreo, calificacion.util)
    return {"ok": True}