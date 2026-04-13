import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="fixture",
    )

def guardar_usuario(nombre, email):
    conexion = get_connection()
    try:
        cursor = conexion.cursor()
        query = "INSERT INTO usuarios (nombre, email) VALUES (%s, %s)"
        cursor.execute(query, (nombre, email))
        conexion.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conexion.close()

def obtener_usuarios_db(limit, offset):
    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)

        query = "SELECT id, nombre, email FROM usuarios LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, offset))
        usuarios = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        total = cursor.fetchone()['total']

        return usuarios, total
    finally:
        cursor.close()
        conexion.close()

def obtener_usuario_id(id_usuario):
    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT id, nombre, email FROM usuarios WHERE id = %s"
        cursor.execute(query, (id_usuario,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()

def reemplazar_usuario(id_usuario, nombre, email):
    conexion = get_connection()
    try:
        cursor = conexion.cursor()
        query = "UPDATE usuarios SET nombre = %s, email = %s WHERE id = %s"
        cursor.execute(query, (nombre, email, id_usuario))
        conexion.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conexion.close()

def eliminar_usuario_db(id_usuario):
    conexion = get_connection()
    try:
        cursor = conexion.cursor()
        query = "DELETE FROM usuarios WHERE id = %s"
        cursor.execute(query, (id_usuario,))
        conexion.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conexion.close()

def actualizar_resultado_partido(id_partido, goles_local, goles_visitante):
    conexion = get_connection()
    try:
        cursor = conexion.cursor()
        query = "UPDATE partidos SET goles_local = %s, goles_visitante = %s WHERE id = %s"
        cursor.execute(query, (goles_local, goles_visitante, id_partido))
        conexion.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conexion.close()