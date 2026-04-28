from flask import Flask, render_template, request, redirect, url_for
import pyodbc
import qrcode
import io
import base64
import json
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=localhost,1433;"
        "DATABASE=Zoologico;"
        "UID=SA;"
        "PWD=TuPassword123!;"
        "TrustServerCertificate=yes;"
    )
    conn = pyodbc.connect(connection_string)
    return conn

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

@app.route('/')
def index():
    sucursales = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE'")
        tablas = cursor.fetchall()
        print("=== TABLAS EN LA BD ===")
        for t in tablas:
            print(t[0])
        print("=======================")
        cursor.execute("SELECT id_zoologico, Nombre, Ciudad FROM Zoologico.Zoologico")
        sucursales = cursor.fetchall()
        conn.close()
    except Exception as e:
        print("Error al obtener sucursales:", e)
        sucursales = [
            {'id': 1, 'nombre': 'Zoo Central (Demo)', 'ubicacion': 'Ciudad de México'},
            {'id': 2, 'nombre': 'Zoo Safari (Demo)',  'ubicacion': 'Monterrey'}
        ]
    return render_template('index.html', sucursales=sucursales)

@app.route('/nosotros')
def about():
    return render_template('nosotros.html')

@app.route('/comprar/<sucursal_id>', methods=['GET', 'POST'])
def comprar_boleto(sucursal_id):
    if request.method == 'POST':
        nombre_visitante = request.form['nombre_visitante']
        tipo_boleto      = request.form['tipo_boleto']
        cantidad         = int(request.form['cantidad'])
        fecha_compra     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        nuevo_id = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                           INSERT INTO dbo.Boletos (sucursal_id, nombre_visitante, tipo_boleto, cantidad)
                               OUTPUT INSERTED.id
                           VALUES (?, ?, ?, ?)
                           ''', (sucursal_id, nombre_visitante, tipo_boleto, cantidad))
            row = cursor.fetchone()
            if row:
                nuevo_id = row[0]
            conn.commit()
            conn.close()
        except Exception as e:
            print("Error al guardar el boleto (usando ID de demo):", e)
            nuevo_id = f"DEMO-{int(datetime.now().timestamp())}"

        datos_boleto = {
            "boleto_id":   nuevo_id,
            "sucursal_id": sucursal_id,
            "visitante":   nombre_visitante,
            "tipo":        tipo_boleto,
            "cantidad":    cantidad,
            "fecha":       fecha_compra,
        }

        qr_base64 = generar_qr_base64(datos_boleto)

        return render_template(
            'boleto_confirmacion.html',
            boleto=datos_boleto,
            qr_base64=qr_base64
        )

    return render_template('create_ticket.html', sucursal_id=sucursal_id)

if __name__ == '__main__':
    app.run(debug=True, port=5000)