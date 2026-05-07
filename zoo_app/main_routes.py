from flask import Blueprint, render_template, request, redirect, url_for, flash
from zoo_app.db import get_db
import uuid
from datetime import datetime
import json
import qrcode
import io
import base64

bp = Blueprint('main', __name__)

def generar_qr_base64(datos: dict) -> str:
    contenido = json.dumps(datos, ensure_ascii=False)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=3,
    )
    qr.add_data(contenido)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

@bp.route('/')
def index():
    sucursales = []
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id_zoologico, Nombre, Ciudad FROM Zoologico.Zoologico")
        sucursales = cursor.fetchall()
    except Exception as e:
        flash("No se pudieron cargar las sucursales en este momento. Intente más tarde.", "error")

    return render_template('index.html', sucursales=sucursales)

@bp.route('/nosotros')
def about():
    return render_template('nosotros.html')

@bp.route('/comprar/<string:sucursal_id>', methods=['GET', 'POST'])
def comprar_boleto(sucursal_id):
    if request.method == 'POST':
        nombre_visitante = request.form.get('nombre_visitante', '').strip()
        tipo_boleto      = request.form.get('tipo_boleto', '').strip()
        correo           = request.form.get('correo', '').strip()
        telefono         = request.form.get('telefono', '').strip()

        try:
            cantidad = int(request.form.get('cantidad', 1))
        except ValueError:
            flash("La cantidad debe ser un número válido.", "error")
            return redirect(url_for('main.comprar_boleto', sucursal_id=sucursal_id))

        if not nombre_visitante or not tipo_boleto or not correo or not telefono:
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for('main.comprar_boleto', sucursal_id=sucursal_id))

        fecha_compra = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nuevo_id_boleto = str(uuid.uuid4())

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO Zoologico.Tabla_boleto
                           (Id_boleto, Id_zoologico, Nombre_usuario, Correo_electronico, N_telefono)
                           VALUES (?, ?, ?, ?, ?)
                           ''', (nuevo_id_boleto, sucursal_id, nombre_visitante, correo, telefono))
            conn.commit()
        except Exception as e:
            flash("Ocurrió un error al procesar su compra. Por favor, intente de nuevo.", "error")
            return redirect(url_for('main.comprar_boleto', sucursal_id=sucursal_id))

        datos_boleto = {
            "boleto_id":   nuevo_id_boleto,
            "sucursal_id": sucursal_id,
            "visitante":   nombre_visitante,
            "tipo":        tipo_boleto,
            "cantidad":    cantidad,
            "fecha":       fecha_compra,
        }

        qr_base64 = generar_qr_base64(datos_boleto)

        flash("¡Compra realizada con éxito!", "success")
        return render_template(
            'boleto_confirmacion.html',
            boleto=datos_boleto,
            qr_base64=qr_base64
        )

    return render_template('create_ticket.html', sucursal_id=sucursal_id)
