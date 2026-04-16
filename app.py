from flask import Flask, render_template, request, redirect, url_for
import pyodbc
import uuid

app = Flask(__name__)

# Función para obtener la conexión a la base de datos
def get_db_connection():
    connection_string = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=127.0.0.1,1433;"
        "DATABASE=Zoologico;"
        "UID=sa;"
        "PWD=TuPasswordSeguro123!;"
        "TrustServerCertificate=yes;"
    )
    conn = pyodbc.connect(connection_string)
    return conn

# 1. Mostrar sucursales (READ parcial de la tabla Zoologico)
@app.route('/')
def index():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Id_zoologico, Nombre, Ciudad, Pais FROM Zoologico.Zoologico")
        sucursales = cursor.fetchall()
        conn.close()
    except Exception as e:
        print("Error al obtener zoologicos o la tabla no existe:", e)
        # Mock de datos si aún no hay base de datos o da error
        sucursales = [
            {'Id_zoologico': '11111111-1111-1111-1111-111111111111', 'Nombre': 'Zoo Central (Demo)', 'Ciudad': 'Ciudad de México', 'Pais': 'México'},
            {'Id_zoologico': '22222222-2222-2222-2222-222222222222', 'Nombre': 'Zoo Safari (Demo)', 'Ciudad': 'Monterrey', 'Pais': 'México'}
        ]
        
    return render_template('index.html', sucursales=sucursales)

# 2. Venta de boletos (CREATE en Tabla_boleto)
@app.route('/comprar/<string:id_zoologico>', methods=['GET', 'POST'])
def comprar_boleto(id_zoologico):
    nombre_zoo = "Desconocido"
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Nombre FROM Zoologico.Zoologico WHERE Id_zoologico = ?", (id_zoologico,))
        row = cursor.fetchone()
        if row:
            nombre_zoo = row[0]
        conn.close()
    except Exception as e:
        print("No se pudo obtener el nombre del zoológico:", e)

    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        correo_electronico = request.form['correo_electronico']
        n_telefono = request.form['n_telefono']
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            id_boleto = str(uuid.uuid4())

            cursor.execute('''
                INSERT INTO Zoologico.Tabla_boleto (Id_boleto, Id_zoologico, Nombre_usuario, Correo_electronico, N_telefono)
                VALUES (?, ?, ?, ?, ?)
            ''', (id_boleto, id_zoologico, nombre_usuario, correo_electronico, n_telefono))
            
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        except Exception as e:
            print("Error al guardar el boleto:", e)
            return f"Ocurrió un error al guardar el boleto: {e}"

    # Mostrar el formulario
    return render_template('create_ticket.html', id_zoologico=id_zoologico, nombre_zoo=nombre_zoo)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
