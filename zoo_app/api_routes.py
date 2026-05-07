from flask import Blueprint, jsonify
from zoo_app.db import get_db

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/validar/<boleto_id>', methods=['GET'])
def validar_acceso(boleto_id):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT Nombre_usuario, Id_zoologico
                       FROM Zoologico.Tabla_boleto
                       WHERE Id_boleto = ?
                       ''', (boleto_id,))
        registro = cursor.fetchone()

        if registro:
            return jsonify({
                "valido": True,
                "mensaje": "Acceso permitido",
                "visitante": registro[0],
                "sucursal": registro[1]
            }), 200
        else:
            return jsonify({
                "valido": False,
                "mensaje": "Boleto no encontrado o inválido"
            }), 404

    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500
