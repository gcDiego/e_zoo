from flask import Flask, render_template, request, redirect, url_for
import pyodbc

app = Flask(__name__)

# Función para obtener la conexión a la base de datos
def get_db_connection():
    server = 'localhost'
    database = 'Zoologico'
    username = 'sa'
    password = 'PassWORD123!'
    # Nota: Agregamos TrustServerCertificate=yes para evitar problemas locales con certificados en ODBC 18
    connection_string = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=yes;'
    conn = pyodbc.connect(connection_string)
    return conn

# 1. Mostrar sucursales (READ parcial)
@app.route('/')
def index():
    sucursales = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, ubicacion FROM Sucursales")
        sucursales = cursor.fetchall()
        conn.close()
    except Exception as e:
        print("Error al obtener sucursales o la tabla no existe:", e)
        # Mock de datos para que puedas visualizar la página si aún no hay base de datos
        sucursales = [
            {'id': 1, 'nombre': 'Zoo Central (Demo)', 'ubicacion': 'Ciudad de México'},
            {'id': 2, 'nombre': 'Zoo Safari (Demo)', 'ubicacion': 'Monterrey'}
        ]
        
    return render_template('index.html', sucursales=sucursales)

# 2. Venta de boletos (CREATE)
@app.route('/comprar/<int:sucursal_id>', methods=['GET', 'POST'])
def comprar_boleto(sucursal_id):
    if request.method == 'POST':
        nombre_visitante = request.form['nombre_visitante']
        tipo_boleto = request.form['tipo_boleto']
        cantidad = request.form['cantidad']
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Insertar en la tabla Boletos
            cursor.execute('''
                INSERT INTO Boletos (sucursal_id, nombre_visitante, tipo_boleto, cantidad)
                VALUES (?, ?, ?, ?)
            ''', (sucursal_id, nombre_visitante, tipo_boleto, cantidad))
            
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        except Exception as e:
            print("Error al guardar el boleto:", e)
            return f"Ocurrió un error al guardar el boleto: {e}"

    # Mostrar el formulario
    return render_template('create_ticket.html', sucursal_id=sucursal_id)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
