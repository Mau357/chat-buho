from fastapi import APIRouter
from pydantic import BaseModel

from ..services.groq_service import generar_sql, formatear_respuesta
from ..database.conection import ejecutar_query

router = APIRouter()

class Mensaje(BaseModel):
    texto: str

@router.post("/chat")
def chat(mensaje: Mensaje):
    # 1. Convertir pregunta a SQL
    sql = generar_sql(mensaje.texto)

    # 2. Validar que solo sea SELECT
    if not sql.lower().startswith("select"):
        return {"respuesta": "Solo se permiten consultas de consulta (SELECT)."}

    # 3. Ejecutar SQL en la base de datos
    try:
        datos = ejecutar_query(sql)
    except Exception as e:
        return {"respuesta": f"Error al consultar la base de datos: {str(e)}"}

    # 4. Formatear respuesta en lenguaje natural
    try:
        respuesta_natural = formatear_respuesta(mensaje.texto, datos)
    except Exception as e:
        return {"respuesta": f"Error al formatear respuesta: {str(e)}"}

    return {
        "respuesta": respuesta_natural
    }