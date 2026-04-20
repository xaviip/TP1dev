import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="fixture",
    )

#Pre:recibe dos strings no vacios
#Post: devuelve True si existe un partido con el equipo local y visitante dados, False caso contrario
def existe_partido(local, visitante):
    conexion = get_connection()
    try:
        cursor = conexion.cursor(buffered=True)
        query = """
            SELECT id FROM partidos 
            WHERE equipo_local = %s AND equipo_visitante = %s
            LIMIT 1
        """
        cursor.execute(query, (local, visitante))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conexion.close()

# Pre: local, visitante, estadio, ciudad, fase no vacíos. fecha en formato 'YYYY-MM-DD'.
# Post: inserta el partido en la tabla y retorna el ID generado.
def guardar_partido(local, visitante, fecha, fase, estadio, ciudad):
    conexion = get_connection()
    try:
        cursor = conexion.cursor()
        query = """
            INSERT INTO partidos (equipo_local, equipo_visitante, fecha, fase, estadio, ciudad) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (local, visitante, fecha, fase, estadio, ciudad))
        conexion.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conexion.close()

#Pre:limit > 0 y offset >= 0, fase, equipo y fecha pueden ser None o strings no vacíos
#Post: retorna una tupla con la lista de partidos y el total de registros encontrados
def obtener_partidos_db(limit, offset, fase=None, equipo=None, fecha=None):
    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)

        query_base = "SELECT id, equipo_local, equipo_visitante, fecha, fase, local, visitante FROM partidos"
        count_base = "SELECT COUNT(*) as total FROM partidos"

        condiciones = []
        valores = []

        if fase:
            condiciones.append("fase = %s")
            valores.append(fase)

        if equipo:
            condiciones.append("(equipo_local = %s OR equipo_visitante = %s)")
            valores.extend([equipo, equipo])

        if fecha:
            condiciones.append("DATE(fecha) = %s")
            valores.append(fecha)

        clausula_where = ""
        if condiciones:
            clausula_where = " WHERE " + " AND ".join(condiciones)
            query_base += clausula_where
            count_base += clausula_where

        cursor.execute(count_base, tuple(valores))
        total = cursor.fetchone()['total']

        query_final = query_base + " LIMIT %s OFFSET %s"
        valores_final = valores + [limit, offset]

        cursor.execute(query_final, tuple(valores_final))
        partidos = cursor.fetchall()

        return partidos, total
    finally:
        cursor.close()
        conexion.close()


#Pre: id_partido debe ser un entero
#Post: devuelve un diccionario con los datos del partido, o None si no se encuentra
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

#Pre:recibe un id_partidito debiendo ser entero, local, visitante, fecha y fase no pueden ser strings vacíos
#Post:devuelve true si la acttualización de los campos en la tabla partidos se registró con exito a traves del id_partidito, false si no se encontró
def reemplazar_partido_db(id_partidito, local, visitante, fecha, fase):
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
        cursor.execute(query, (local, visitante, fecha, fase, id_partidito))
        conexion.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conexion.close()

#Pre:id_partido debe ser un entero
#Post: elimina el partido con el ID dado, retorna True si se eliminó, False caso contrario
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

#Pre: id_partido debe ser un entero, goles_l y goles_v representando el marcador
#Post: true si se encontró el registro y se actualizó la fila, false si el id no existe en la BD
def actualizar_resultado_db(id_p, goles_l, goles_v):
    conexion = get_connection()
    try:
        cursor = conexion.cursor()
        query = "UPDATE partidos SET local = %s, visitante = %s WHERE id = %s"
        cursor.execute(query, (goles_l, goles_v, id_p))
        conexion.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conexion.close()

# Pre: recibe id_usuario e id_partido como enteros.
# Post: retorna True si ya existe una predicción de ese usuario para ese partido, False si no.
def existe_prediccion_db(id_usuario, id_partido):
    conexion = get_connection()
    try:
        cursor = conexion.cursor(buffered=True)
        query = "SELECT 1 FROM predicciones WHERE id_usuario = %s AND id_partido = %s"
        cursor.execute(query, (id_usuario, id_partido))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conexion.close()

# Pre: recibe IDs de usuario, partido y goles predichos >=0.
# Post: inserta la predicción en la base de datos.
def guardar_prediccion_db(id_usuario, id_partido, goles_l, goles_v):
    conexion = get_connection()
    try:
        cursor = conexion.cursor()
        query = """
            INSERT INTO predicciones (id_usuario, id_partido, local, visitante)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (id_usuario, id_partido, goles_l, goles_v))
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()

# Pre: id_usuario debe ser un número entero positivo, limite debe ser un entero mayor a 0 y desplazamiento un entero mayor o igual a 0 .
# Post: retorna una tupla conteniendo: 1) una lista de diccionarios con los datos de las predicciones
#       (id, id_partido, local, visitante) y 2) el número total de registros
#       encontrados para ese usuario en la bd
def obtener_predicciones_usuario_db(id_usuario, limite, desplazamiento):
    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)

        query = "SELECT id, id_partido, local, visitante FROM predicciones WHERE id_usuario = %s LIMIT %s OFFSET %s"
        cursor.execute(query, (id_usuario, limite, desplazamiento))

        predicciones = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) as total FROM predicciones WHERE id_usuario = %s", (id_usuario,))
        total = cursor.fetchone()['total']

        return predicciones, total
    finally:
        cursor.close()
        conexion.close()

#Pre: id_partido debe ser un entero.
#Post: Retorna True si el partido no tiene resultados cargados aún (está disponible), False si ya se jugó.
def verificar_partido_disponible_db(id_partido):
    conexion = get_connection()
    try:
        cursor = conexion.cursor(buffered=True)
        query = "SELECT id FROM partidos WHERE id = %s AND fecha > NOW()"
        cursor.execute(query, (id_partido,))

        resultado = cursor.fetchone()
        return resultado is not None
    finally:
        cursor.close()
        conexion.close()

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
#Post: devuelve un diccionario con los datos del usuario, o None si no lo encuentra
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


#Pre: limit > 0 y offset >= 0.
#Post: Retorna una tupla (lista_ranking, total_registros). Cada elemento de la lista contiene 'id_usuario' y 'puntos' totales calculados según el reglamento.
def obtener_ranking_db(limit, offset):
    conexion = get_connection()
    try:
        cursor = conexion.cursor(dictionary=True)
        query_ranking = """
            SELECT prediccion.id_usuario, SUM(
                CASE 
                    WHEN prediccion.local = partidito.local AND prediccion.visitante = partidito.visitante THEN 3
                    WHEN (prediccion.local > prediccion.visitante AND partidito.local > partidito.visitante) OR 
                         (prediccion.local < prediccion.visitante AND partidito.local < partidito.visitante) OR 
                         (prediccion.local = prediccion.visitante AND partidito.local = partidito.visitante) THEN 1
                    ELSE 0 
                END
            ) AS puntos
            FROM predicciones prediccion
            JOIN partidos partidito ON prediccion.id_partido = partidito.id
            WHERE partidito.local IS NOT NULL
            GROUP BY prediccion.id_usuario
            ORDER BY puntos DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(query_ranking, (limit, offset))
        ranking = cursor.fetchall()

        cursor.execute("SELECT COUNT(DISTINCT id_usuario) FROM predicciones")
        total = cursor.fetchone()['COUNT(DISTINCT id_usuario)']

        return ranking, total
    finally:
        cursor.close()
        conexion.close()