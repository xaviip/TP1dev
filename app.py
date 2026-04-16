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
    actualizar_partido_db,
    eliminar_partido_db,
    actualizar_resultado_db, existe_partido
)

app = Flask(__name__)
app.json.sort_keys = False

@app.errorhandler(mysql.connector.Error)
def handle_db_error(err):
    if err.errno == 1062:
        return jsonify({"error": "Conflicto: El email ya está registrado"}), 409
    return jsonify({"error": f"Error de base de datos: {str(err)}"}), 500


@app.errorhandler(Exception)
def handle_general_exception(err):
    return jsonify({"error": "Error interno del servidor", "detalle": str(err)}), 500


@app.route('/')
def home():
    return jsonify({"mensaje": "Bienvenido a la API de gestión de partidos de fútbol"}), 200

#Pre: recibe un JSON con los campos 'nombre' y 'email' no vacíos
#Post: retorna un JSON con el mensaje de éxito si son correctos el ID del usuario creado, su nombre y email, o un error si faltan datos
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

#Pre:-
#Post: devuelve una lista de usuarios y links de navegación HATEOAS
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

#Pre:se le pasa por parámetro un ID
#Post: devuelve 200 si obtiene el usuario, 404 si no lo encuentra
@app.route('/usuarios/<int:id>', methods=['GET'])
def obtener_usuario(id):
    usuario = obtener_usuario_id(id)
    if usuario:
        return jsonify(usuario), 200
    return jsonify({"error": "Usuario no encontrado"}), 404

#Pre:se le pasa por parámetro un ID y un JSON con los campos 'nombre' y 'email' no vacíos
#Post: actualiza el usuario con el ID dado, retorna 204 si se actualizó
@app.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    datos = request.get_json()

    if not datos or not datos.get('nombre') or not datos.get('email'):
        return jsonify({"error": "Faltan completar los datos o están vacíos"}), 400

    if reemplazar_usuario(id, datos['nombre'], datos['email']):
        return '', 204
    return jsonify({"error": "Usuario no encontrado"}), 404

#Pre: se le pasa por parámetro un ID
#Post: elimina el usuario con el ID dado, retorna 204 si se eliminó,
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    if eliminar_usuario_db(id):
        return '', 204
    return jsonify({"error": "Usuario no encontrado"}), 404


@app.route('/partidos', methods=['POST'])
def crear_partido():
    datos = request.get_json()
    campos = ['equipo_local', 'equipo_visitante', 'fecha', 'fase']

    if not datos or any(not datos.get(c) for c in campos):
        return jsonify({"error": "Faltan completar datos obligatorios"}), 400

    local = datos['equipo_local'].strip()
    visitante = datos['equipo_visitante'].strip()

    if local.lower() == visitante.lower():
        return jsonify({"error": "Lógica inválida: Un equipo no puede jugar contra sí mismo"}), 400

    if existe_partido(local, visitante):
        return jsonify({"error": "Conflicto: Este partido ya se encuentra registrado."}), 409

    id_creado = guardar_partido(local, visitante, datos['fecha'], datos['fase'])
    return jsonify({"mensaje": "Partido creado correctamente", "id": id_creado}), 201


@app.route('/partidos', methods=['GET'])
def listar_partidos():
    limit_str = request.args.get('_limit', '10')
    offset_str = request.args.get('_offset', '0')
    fase_filtro = request.args.get('fase')
    equipo_filtro = request.args.get('equipo')
    fecha_filtro = request.args.get('fecha')

    if not limit_str.isdigit() or not offset_str.isdigit():
        return jsonify({"error": "Los parámetros deben ser números enteros"}), 400

    limit, offset = int(limit_str), int(offset_str)

    partidos, total = obtener_partidos_db(limit, offset, fase_filtro, equipo_filtro, fecha_filtro)

    base_url = request.base_url
    last_off = max(0, ((total - 1) // limit) * limit) if total > 0 else 0

    filtros = ""
    if fase_filtro: filtros += f"fase={fase_filtro}&"
    if equipo_filtro: filtros += f"equipo={equipo_filtro}&"
    if fecha_filtro: filtros += f"fecha={fecha_filtro}&"

    _links = {
        "_first": {"href": f"{base_url}?{filtros}_offset=0&_limit={limit}"},
        "_prev": {
            "href": f"{base_url}?{filtros}_offset={max(0, offset - limit)}&_limit={limit}"} if offset > 0 else None,
        "_next": {"href": f"{base_url}?{filtros}_offset={offset + limit}&_limit={limit}"} if (offset + limit) < total else None,
        "_last": {"href": f"{base_url}?{filtros}_offset={last_off}&_limit={limit}"}
    }

    return jsonify({
      "partidos": partidos,
      "_links": _links
    }), 200

@app.route('/partidos/<int:id>', methods=['GET'])
def obtener_partido(id):
    partido = obtener_partido_id_db(id)
    if not partido:
        return jsonify({"error": "Partido no encontrado"}), 404
    return jsonify(partido), 200


@app.route('/partidos/<int:id>', methods=['PUT'])
def actualizar_partido(id):
    datos = request.get_json()
    campos = ['equipo_local', 'equipo_visitante', 'fecha', 'fase']

    if not datos or any(not datos.get(c) for c in campos):
        return jsonify({"error": "Datos incompletos para actualizar"}), 400

    if actualizar_partido_db(id, datos['equipo_local'], datos['equipo_visitante'], datos['fecha'], datos['fase']):
        return '', 204
    return jsonify({"error": "Partido no encontrado"}), 404


@app.route('/partidos/<int:id>', methods=['DELETE'])
def borrar_partido(id):
    if eliminar_partido_db(id):
        return '', 204
    return jsonify({"error": "Partido no encontrado"}), 404

#Pre: se le pasa por parámetro un ID y un JSON con los goles del equipo local y visitante.
#Post: actualiza el resultado del partido retornando 204 si se actualizó, 404 si no se encontró, o 400 si faltan datos o son inválidos.
@app.route('/partidos/<int:id>/resultado', methods=['PUT'])
def cargar_resultado(id):
    datos = request.get_json()
    if not datos or 'local' not in datos or 'visitante' not in datos:
        return jsonify({"error": "Se requieren campos 'local' y 'visitante'"}), 400

    if actualizar_resultado_db(id, datos['local'], datos['visitante']):
        return jsonify({"mensaje": "Resultado actualizado correctamente"}), 204
    return jsonify({"error": "Partido no encontrado"}), 404


if __name__ == '__main__':
    app.run(port=5000, debug=True)