import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="fixture",
    )

#Pre: nombre y email no pueden ser strings vacíos
#Post: inserta el usuario en la BD y retorna un diccionario con sus datos e ID
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

#Pre: para la paginación, limit > 0 y offset >= 0
#Post: retorna una lista de usuarios limitada por los parámetros
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

#Pre: id_usuario debe ser un entero
#Post: retorna True si se eliminó el registro, False en caso contrario
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

#Pre: id_usuario debe ser un entero, nombre y email no pueden ser strings vacíos
#Post: actualiza el usuario con el ID dado, retorna True si se actualizó, False caso contrario
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

#Pre: id_usuario debe ser un entero
#Post: elimina el usuario con el ID dado, retorna True si se eliminó, False caso contrario
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


def guardar_partido(local, visitante, fecha, fase):
    conexion = get_connection()
    try:
        cursor = conexion.cursor()
        query = "INSERT INTO partidos (equipo_local, equipo_visitante, fecha, fase) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (local, visitante, fecha, fase))
        conexion.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conexion.close()


def obtener_partidos_db(limit, offset):
    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)
        query = """
                SELECT id, equipo_local, equipo_visitante, fecha, fase, goles_local, goles_visitante
                FROM partidos
                LIMIT %s OFFSET %s \
                """
        cursor.execute(query, (limit, offset))
        partidos = cursor.fetchall()

        cursor.execute("SELECT COUNT(*) as total FROM partidos")
        total = cursor.fetchone()['total']
        return partidos, total
    finally:
        cursor.close()
        conexion.close()


def obtener_partido_id_db(id_partido):
    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT * FROM partidos WHERE id = %s"
        cursor.execute(query, (id_partido,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conexion.close()


def actualizar_partido_db(id_p, local, visitante, fecha, fase):
    conexion = get_connection()
    try:
        cursor = conexion.cursor()
        query = """
                UPDATE partidos
                SET equipo_local     = %s, \
                    equipo_visitante = %s, \
                    fecha            = %s, \
                    fase             = %s
                WHERE id = %s \
                """
        cursor.execute(query, (local, visitante, fecha, fase, id_p))
        conexion.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conexion.close()


def eliminar_partido_db(id_partido):
    conexion = get_connection()
    try:
        cursor = conexion.cursor()
        query = "DELETE FROM partidos WHERE id = %s"
        cursor.execute(query, (id_partido,))
        conexion.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conexion.close()


def actualizar_resultado_db(id_p, goles_l, goles_v):
    conexion = get_connection()
    try:
        cursor = conexion.cursor()
        query = "UPDATE partidos SET goles_local = %s, goles_visitante = %s WHERE id = %s"
        cursor.execute(query, (goles_l, goles_v, id_p))
        conexion.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conexion.close()




