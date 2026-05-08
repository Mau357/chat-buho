from fastapi import APIRouter
from pydantic import BaseModel

from ..services.groq_service import generar_sql, formatear_respuesta, es_respuesta_sin_datos, respuesta_sin_datos
from ..database.conection import ejecutar_query, guardar_sin_respuesta

router = APIRouter()

class Mensaje(BaseModel):
    texto: str

@router.post("/chat")
def chat(mensaje: Mensaje):
    # 1. Generar SQL
    sql = generar_sql(mensaje.texto)

    # 2. Ejecutar SQL
    try:
        datos = ejecutar_query(sql)
    except Exception as e:
        return {"respuesta": f"Error al consultar la base de datos: {str(e)}"}

    # 3. Detectar si no hay datos reales
    if es_respuesta_sin_datos(datos):
        guardar_sin_respuesta(mensaje.texto)
        return {"respuesta": respuesta_sin_datos(mensaje.texto)}

    # 4. Formatear respuesta natural
    try:
        respuesta_natural = formatear_respuesta(mensaje.texto, datos)
    except Exception as e:
        return {"respuesta": f"Error al formatear respuesta: {str(e)}"}

    return {"respuesta": respuesta_natural}