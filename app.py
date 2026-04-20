from flask import Flask, request, jsonify
import mysql.connector
from db import (
    guardar_usuario,
    obtener_usuarios_db,
    obtener_usuario_id,
    reemplazar_usuario,
    eliminar_usuario_db,
    guardar_partido,
    obtener_partidos_db,
    obtener_partido_id_db,
    reemplazar_partido_db,
    eliminar_partido_db,
    actualizar_resultado_db,
    existe_partido,
    existe_prediccion_db,
    guardar_prediccion_db,
    obtener_predicciones_usuario_db,
    verificar_partido_disponible_db,
    obtener_ranking_db
)

app = Flask(__name__)
app.json.sort_keys = False


@app.errorhandler(mysql.connector.Error)
def manejo_error_db(err):
    if err.errno == 1062:
        return jsonify({"error": "Conflicto: El email ya está registrado"}), 409
    return jsonify({"error": f"Error de base de datos: {str(err)}"}), 500


@app.errorhandler(Exception)
def manejo_general_exception(err):
    return jsonify({"error": "Error interno del servidor", "detalle": str(err)}), 500


@app.route('/')
def home():
    return jsonify(
        {"mensaje": "Bienvenido a la API para gestionar partidos con soporte para paginación y fases del torneo."}), 200


# Pre:-
# Post: devuelve un json con la lista de partidos y links de navegación HATEOAS, o un error si los parámetros son inválidos
@app.route('/partidos', methods=['GET'])
def listar_partidos():
    limit_str = request.args.get('_limit', '10')
    offset_str = request.args.get('_offset', '0')
    fase_filtro = request.args.get('fase')
    equipo_filtro = request.args.get('equipo')
    fecha_filtro = request.args.get('fecha')

    if not limit_str.isdigit() or not offset_str.isdigit():
        return jsonify({"error": "Los parámetros deben ser números enteros"}), 400

    fases_validas = ["fase de grupos", "dieciseisavos", "octavos de final", "cuartos de final", "semifinales", "final"]
    if fase_filtro and fase_filtro not in fases_validas:
        return jsonify({"error": f"Fase inválida. Las fases válidas son: {', '.join(fases_validas)}"}), 400

    limit, offset = int(limit_str), int(offset_str)
    partidos, total = obtener_partidos_db(limit, offset, fase_filtro, equipo_filtro, fecha_filtro)
    if total == 0:
        return '', 204
    if not partidos:
        return jsonify({"error": "No se encontraron partidos para los criterios especificados"}), 404

    base_url = request.base_url
    filtros = ""
    if fase_filtro: filtros += f"fase={fase_filtro}&"
    if equipo_filtro: filtros += f"equipo={equipo_filtro}&"
    if fecha_filtro: filtros += f"fecha={fecha_filtro}&"

    last_off = max(0, ((total - 1) // limit) * limit) if total > 0 else 0

    _links = {
        "_first": {"href": f"{base_url}?{filtros}_offset=0&_limit={limit}"},
        "_prev": {
            "href": f"{base_url}?{filtros}_offset={max(0, offset - limit)}&_limit={limit}"} if offset > 0 else None,
        "_next": {"href": f"{base_url}?{filtros}_offset={offset + limit}&_limit={limit}"} if (
                                                                                                         offset + limit) < total else None,
        "_last": {"href": f"{base_url}?{filtros}_offset={last_off}&_limit={limit}"}
    }

    return jsonify({
        "partidos": partidos,
        "_links": _links
    }), 200


# Pre: el body del request debe contener un JSON con los campos 'equipo_local', 'equipo_visitante', 'fecha' y 'fase'
# Post: 200:si los datos son váliidos y no hay duplicados. 400: datos inválidos. 409: si el partido ya existe.500: error de base de datos.
@app.route('/partidos', methods=['POST'])
def crear_partido():
    datos = request.get_json()
    campos = ['equipo_local', 'equipo_visitante', 'fecha', 'fase', 'estadio', 'ciudad']

    for campo in campos:
        if campo not in datos or not datos[campo]:
            return jsonify({"error": f"El campo '{campo}' es obligatorio"}), 400

    if existe_partido(datos['equipo_local'], datos['equipo_visitante']):
        return jsonify({"error": "El partido ya existe"}), 409

    id_nuevo = guardar_partido(
        datos['equipo_local'],
        datos['equipo_visitante'],
        datos['fecha'],
        datos['fase'],
        datos['estadio'],
        datos['ciudad']
    )
    return jsonify({"id": id_nuevo, "mensaje": "Partido creado"}), 201


# Pre: -
# Post: devuelve 400 si el ID es inválido. 200 si obtiene el partido, 404 si no lo encuentra
@app.route('/partidos/<int:id>', methods=['GET'])
def obtener_partido(id):
    if id <= 0:
        return jsonify({"error": "ID inválido. Debe ser un número entero positivo."}), 400
    partido = obtener_partido_id_db(id)
    if not partido:
        return jsonify({"error": "Partido no encontrado"}), 404
    return jsonify(partido), 200


# Pre:recibe un ID por parámetro y se espera un request body en formato JSON conteniendo todos los campos obligatorios del partido base
# Post: 204 si se actualizó, 400 datos incompletos o es nulo
@app.route('/partidos/<int:id>', methods=['PUT'])
def reemplazar_partido(id):
    datos = request.get_json()
    campos = ['equipo_local', 'equipo_visitante', 'fecha', 'fase']

    if not datos or any(not datos.get(campo) for campo in campos):
        return jsonify({"error": "Datos incompletos para el reemplazo"}), 400

    reemplazar_partido_db(id, datos['equipo_local'], datos['equipo_visitante'], datos['fecha'], datos['fase'])
    return '', 204


# Pre: -
# Post: si el id es inválido, retorna 400. Si el partido no existe, retorna 404. Si se actualiza correctamente, retorna 204.
@app.route('/partidos/<int:id>', methods=['DELETE'])
def borrar_partido(id):
    if id <= 0:
        return jsonify({"error": "ID inválido. Debe ser un número entero positivo."}), 400
    if eliminar_partido_db(id):
        return '', 204
    return jsonify({"error": "Partido no encontrado"}), 404


# Pre: se le pasa por parámetro un ID y un JSON con los goles del equipo local y visitante.
# Post: actualiza el resultado del partido retornando 204 si se actualizó, 404 si no se encontró, o 400 si faltan datos o son inválidos.
@app.route('/partidos/<int:id>/resultado', methods=['PUT'])
def actualizar_resultado(id):
    datos = request.get_json()
    if not datos or 'local' not in datos or 'visitante' not in datos:
        return jsonify({"error": "Se requieren campos 'local' y 'visitante'"}), 400

    local = datos['local']
    visitante = datos['visitante']

    if type(local) is not int or type(visitante) is not int or local < 0 or visitante < 0:
        return jsonify({"error": "Los goles deben ser números enteros"}), 400

    if actualizar_resultado_db(id, datos['local'], datos['visitante']):
        return '', 204
    return jsonify({"error": "Partido no encontrado"}), 404


#Pre: recibe ID del partido por URL y JSON con id_usuario, local y visitante [6].
#Post: registra la predicción (201) o retorna error si el partido ya se jugó (400) o si ya existe la predicción (409) [6, 7].
@app.route("/partidos/<int:id>/prediccion", methods=["POST"])
def registrar_prediccion(id):
    datos = request.get_json()

    if not datos or not all(k in datos for k in ('id_usuario', 'local', 'visitante')):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    id_usuario = datos['id_usuario']
    local = datos['local']
    visitante = datos['visitante']

    if existe_prediccion_db(id_usuario, id):
        return jsonify({"error": "El usuario ya registró una predicción para este partido"}), 409

    if not obtener_partido_id_db(id):
        return jsonify({"error": "Partido no encontrado"}), 404

    if not verificar_partido_disponible_db(id):
        return jsonify({"error": "El partido ya se jugó, no se aceptan predicciones"}), 400

    guardar_prediccion_db(id_usuario, id, local, visitante)
    return jsonify({"mensaje": "Predicción registrada con éxito"}), 201

# Pre: id_del_usuario debe ser un entero. Se esperan parámetros opcionales _limit y _offset en la URL.
# Post: retorna un objeto JSON con la lista de predicciones paginada y enlaces HATEOAS, código 200.
@app.route("/usuarios/<int:id_del_usuario>/predicciones", methods=["GET"])
def listar_predicciones(id_del_usuario):
    limit = int(request.args.get('_limit', 10))
    offset = int(request.args.get('_offset', 0))

    lista_datos, total_registros = obtener_predicciones_usuario_db(
        id_del_usuario,
        limit,
        offset
    )

    base_url = f"/usuarios/{id_del_usuario}/predicciones"

    last_off = max(0, ((total_registros - 1) // limit) * limit)

    links = {
        "_first": f"{base_url}?_limit={limit}&_offset=0",
        "_last": f"{base_url}?_limit={limit}&_offset={last_off}",
        "_prev": f"{base_url}?_limit={limit}&_offset={max(0, offset - limit)}" if offset > 0 else None,
        "_next": f"{base_url}?_limit={limit}&_offset={offset + limit}" if (offset + limit) < total_registros else None
    }

    return jsonify({
        "predicciones": lista_datos,
        "total": total_registros,
        "_links": links
    }), 200


# Pre: recibe un JSON con los campos 'nombre' y 'email' no vacíos
# Post: retorna un JSON con el mensaje de éxito si son correctos el ID del usuario creado, su nombre y email, o un error si faltan datos
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    datos = request.get_json()

    if not datos or not datos.get('nombre') or not datos.get('email'):
        return jsonify({"error": "Faltan completar los datos o están vacíos"}), 400

    id_creado = guardar_usuario(datos['nombre'], datos['email'])
    return jsonify({
        "mensaje": "Usuario creado correctamente",
        "id": id_creado,
        "nombre": datos['nombre'],
        "email": datos['email']
    }), 201


# Pre:-
# Post: devuelve una lista de usuarios y links de navegación HATEOAS
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    limit_str = request.args.get('_limit', '10')
    offset_str = request.args.get('_offset', '0')

    if not limit_str.isdigit() or not offset_str.isdigit():
        return jsonify({"error": "Los parámetros deben ser números enteros"}), 400

    limit, offset = int(limit_str), int(offset_str)

    usuarios, total = obtener_usuarios_db(limit, offset)

    base_url = request.base_url
    last_off = max(0, ((total - 1) // limit) * limit) if total > 0 else 0

    _links = {
        "_first": {"href": f"{base_url}?_offset=0&_limit={limit}"},
        "_prev": {
        "href": f"{base_url}?_offset={max(0, offset - limit)}&_limit={limit}"} if offset > 0 else None,
        "_next": {"href": f"{base_url}?_offset={offset + limit}&_limit={limit}"} if (offset + limit) < total else None,
        "_last": {"href": f"{base_url}?_offset={last_off}&_limit={limit}"}
    }

    return jsonify({
        "usuarios": usuarios,
        "_links": _links
    }), 200


# Pre:se le pasa por parámetro un ID
# Post: devuelve 200 si obtiene el usuario, 404 si no lo encuentra
@app.route('/usuarios/<int:id>', methods=['GET'])
def obtener_usuario(id):
    usuario = obtener_usuario_id(id)

    if id <= 0:
        return jsonify({"error": "ID inválido. Debe ser un número entero positivo."}), 400

    if usuario:
        return jsonify(usuario), 200

    return jsonify({"error": "Usuario no encontrado"}), 404


# Pre:se le pasa por parámetro un ID y un JSON con los campos 'nombre' y 'email' no vacíos
# Post: actualiza el usuario con el ID dado, retorna 204 si se actualizó
@app.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    datos = request.get_json()

    if id <= 0:
        return jsonify({"error": "ID inválido. Debe ser un número entero positivo."}), 400

    if not datos or not datos.get('nombre') or not datos.get('email'):
        return jsonify({"error": "Faltan completar los datos o están vacíos"}), 400

    if reemplazar_usuario(id, datos['nombre'], datos['email']):
        return '', 204
    return jsonify({"error": "Usuario no encontrado"}), 404


# Pre: se le pasa por parámetro un ID
# Post: elimina el usuario con el ID dado, retorna 204 si se eliminó,
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    if id <= 0:
        return jsonify({"error": "ID inválido. Debe ser un número entero positivo."}), 400

    if eliminar_usuario_db(id):
        return '', 204
    return jsonify({"error": "Usuario no encontrado"}), 404

#Pre: se esperan parámetros opcionales 'limit' y 'offset' en la URL.
#Post: devuelve un JSON con el ranking paginado, total de registros y enlaces HATEOAS.
@app.route('/ranking', methods=['GET'])
def consultar_ranking():
    limit = int(request.args.get('_limit', 10))
    offset = int(request.args.get('_offset', 0))

    datos_ranking, total = obtener_ranking_db(limit, offset)

    if not datos_ranking:
        return '', 204

    base_url = request.base_url
    last_offset = max(0, ((total - 1) // limit) * limit) if total > 0 else 0

    enlaces = {
        "_first": f"{base_url}?limit={limit}&offset=0",
        "_last": f"{base_url}?limit={limit}&offset={last_offset}",
        "_prev": f"{base_url}?limit={limit}&offset={max(0, offset - limit)}" if offset > 0 else None,
        "_next": f"{base_url}?limit={limit}&offset={offset + limit}" if (offset + limit) < total else None
    }

    return jsonify({
        "data": datos_ranking,
        "total": total,
        "_links": enlaces
    }), 200


if __name__ == '__main__':
    app.run(port=5000, debug=True)