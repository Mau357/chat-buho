import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="cocacola345",
        database="chat_buho_final"
    )

def ejecutar_query(query: str):
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute(query)
    resultado = cursor.fetchall()
    cursor.close()
    conexion.close()
    return resultado

def guardar_sin_respuesta(pregunta: str):
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute(
        "INSERT INTO PreguntasSinRespuesta (pregunta) VALUES (%s)",
        (pregunta,)
    )
    conexion.commit()
    cursor.close()
    conexion.close()

def calificar_respuesta(id_monitoreo: int, util: int):  # ← int en lugar de bool
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE Monitoreo SET util = %s WHERE id_monitoreo = %s",
        (util, id_monitoreo)
    )
    conexion.commit()
    cursor.close()
    conexion.close()

def guardar_monitoreo(pregunta, sql_generado, respuesta_final, numero_tokens, exitoso) -> int:
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute(
        """INSERT INTO Monitoreo (pregunta, sql_generado, respuesta_final, numero_tokens, exitoso)
           VALUES (%s, %s, %s, %s, %s)""",
        (pregunta, sql_generado, respuesta_final, numero_tokens, exitoso)
    )
    conexion.commit()
    id_insertado = cursor.lastrowid  # ← retorna el id generado
    cursor.close()
    conexion.close()
    return id_insertado