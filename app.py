from flask import Flask, request, jsonify
import mysql.connector
from db import (
    guardar_usuario,
    obtener_usuarios_db,
    obtener_usuario_id,
    reemplazar_usuario,
    eliminar_usuario_db,
    actualizar_resultado_partido
)

app = Flask(__name__)

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


@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    limit = int(request.args.get('_limit', 10))
    offset = int(request.args.get('_offset', 0))

    usuarios, total = obtener_usuarios_db(limit, offset)

    base_url = request.base_url
    last_offset = max(0, ((total - 1) // limit) * limit) if total > 0 else 0

    _links = {
        "_first": f"{base_url}?_limit={limit}&_offset=0",
        "_last": f"{base_url}?_limit={limit}&_offset={last_offset}",
        "_prev": f"{base_url}?_limit={limit}&_offset={max(0, offset - limit)}" if offset > 0 else None,
        "_next": f"{base_url}?_limit={limit}&_offset={offset + limit}" if (offset + limit) < total else None
    }

    return jsonify({
        "data": usuarios,
        "total": total,
        "_links": _links
    }), 200


@app.route('/usuarios/<int:id>', methods=['GET'])
def obtener_usuario(id):
    usuario = obtener_usuario_id(id)
    if usuario:
        return jsonify(usuario), 200
    return jsonify({"error": "Usuario no encontrado"}), 404


@app.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    datos = request.get_json()

    if not datos or not datos.get('nombre') or not datos.get('email'):
        return jsonify({"error": "Faltan completar los datos o están vacíos"}), 400

    if reemplazar_usuario(id, datos['nombre'], datos['email']):
        return '', 204
    return jsonify({"error": "Usuario no encontrado"}), 404


@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    if eliminar_usuario_db(id):
        return '', 204
    return jsonify({"error": "Usuario no encontrado"}), 404


@app.route('/partidos/<int:id>/resultado', methods=['PUT'])
def cargar_resultado(id):
    datos = request.get_json()

    if not datos or 'local' not in datos or 'visitante' not in datos:
        return jsonify({"error": "Faltan los goles del equipo local o visitante"}), 400

    actualizado = actualizar_resultado_partido(id, datos['local'], datos['visitante'])

    if actualizado:
        return jsonify({"mensaje": "Resultado actualizado correctamente"}), 200
    return jsonify({"error": "Partido no encontrado"}), 404


if __name__ == '__main__':
    app.run(port=5000, debug=True)