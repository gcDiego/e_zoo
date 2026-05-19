from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from zoo_app.db import get_db
from flask_mail import Message
from zoo_app import mail
import uuid
from datetime import datetime
import json
import qrcode
import io
import base64
import threading

bp = Blueprint('main', __name__)

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_ticket_email(recipient, boleto_data, qr_base64):
    """Envía el correo con el boleto y el QR."""
    try:
        app = current_app._get_current_object()
        msg = Message(
            subject="Tu Boleto para e-Zoo",
            recipients=[recipient],
            html=render_template('email/ticket_email.html', boleto=boleto_data)
        )
        # Adjuntar la imagen QR en el cuerpo del correo
        msg.attach(
            filename="qr_code.png",
            content_type="image/png",
            data=base64.b64decode(qr_base64),
            disposition='inline',
            headers={'Content-ID': '<qr_code>'}
        )
        # Enviar correo en un hilo separado para no bloquear la solicitud
        thr = threading.Thread(target=send_async_email, args=[app, msg])
        thr.start()
    except Exception as e:
        app.logger.error(f"Error al enviar correo: {e}")


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
            # Obtener el nombre de la sucursal
            cursor.execute("SELECT Nombre FROM Zoologico.Zoologico WHERE id_zoologico = ?", (sucursal_id,))
            sucursal_nombre = cursor.fetchone()[0]

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
            "sucursal_nombre": sucursal_nombre,
            "visitante":   nombre_visitante,
            "tipo":        tipo_boleto,
            "cantidad":    cantidad,
            "fecha":       fecha_compra,
        }

        qr_base64 = generar_qr_base64(datos_boleto)
        
        # Enviar el correo electrónico
        send_ticket_email(correo, datos_boleto, qr_base64)

        flash("¡Compra realizada con éxito! Recibirás tu boleto por correo electrónico.", "success")
        return render_template(
            'boleto_confirmacion.html',
            boleto=datos_boleto,
            qr_base64=qr_base64
        )

    return render_template('create_ticket.html', sucursal_id=sucursal_id)
