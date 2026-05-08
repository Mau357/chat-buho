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
    """Guarda en PreguntasSinRespuesta cuando el bot no encontró datos."""
    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        "INSERT INTO PreguntasSinRespuesta (pregunta) VALUES (%s)",
        (pregunta,)
    )
    conexion.commit()

    cursor.close()
    conexion.close()