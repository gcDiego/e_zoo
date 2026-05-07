from flask import Blueprint, render_template, flash, request, redirect, url_for
from zoo_app.db import get_db
import uuid

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/boletos')
def dashboard_boletos():
    boletos = []
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT Id_boleto, Id_zoologico, Nombre_usuario, Correo_electronico, N_telefono
                       FROM Zoologico.Tabla_boleto
                       ''')
        boletos = cursor.fetchall()
    except Exception as e:
        flash("No se pudieron cargar los registros de boletos.", "error")

    return render_template('dashboard.html', boletos=boletos)

@bp.route('/scan')
def scan_ticket():
    """Muestra la interfaz de escaneo de boletos."""
    return render_template('scan.html')

@bp.route('/zoologicos')
def list_zoologicos():
    """Muestra una lista de todas las sucursales del zoológico."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id_zoologico, Nombre, Ciudad, Pais, Direccion, Telefono FROM Zoologico.Zoologico")
        zoologicos = cursor.fetchall()
    except Exception as e:
        flash(f"Error al cargar los zoológicos: {e}", "error")
        zoologicos = []
    return render_template('admin/zoo_list.html', zoologicos=zoologicos)

@bp.route('/zoologicos/nuevo', methods=['GET', 'POST'])
def add_zoologico():
    """Muestra el formulario para añadir un nuevo zoológico y procesa el envío."""
    if request.method == 'POST':
        nombre = request.form['nombre']
        ciudad = request.form['ciudad']
        pais = request.form['pais']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        nuevo_id_zoo = str(uuid.uuid4())

        if not nombre or not ciudad or not pais or not direccion:
            flash('Todos los campos marcados con * son obligatorios.', 'error')
            return render_template('admin/zoo_form.html')

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Zoologico.Zoologico (Id_zoologico, Nombre, Ciudad, Pais, Direccion, Telefono) VALUES (?, ?, ?, ?, ?, ?)",
                (nuevo_id_zoo, nombre, ciudad, pais, direccion, telefono)
            )
            conn.commit()
            flash('Zoológico añadido con éxito.', 'success')
            return redirect(url_for('admin.list_zoologicos'))
        except Exception as e:
            flash(f'Error al añadir el zoológico: {e}', 'error')

    return render_template('admin/zoo_form.html', zoo=None)

@bp.route('/zoologicos/<string:id>/editar', methods=['GET', 'POST'])
def edit_zoologico(id):
    """Muestra el formulario para editar un zoológico y procesa la actualización."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Zoologico.Zoologico WHERE id_zoologico = ?", (id,))
    zoo = cursor.fetchone()

    if not zoo:
        flash('Zoológico no encontrado.', 'error')
        return redirect(url_for('admin.list_zoologicos'))

    if request.method == 'POST':
        nombre = request.form['nombre']
        ciudad = request.form['ciudad']
        pais = request.form['pais']
        direccion = request.form['direccion']
        telefono = request.form['telefono']

        if not nombre or not ciudad or not pais or not direccion:
            flash('Todos los campos marcados con * son obligatorios.', 'error')
            return render_template('admin/zoo_form.html', zoo=zoo)

        try:
            cursor.execute(
                "UPDATE Zoologico.Zoologico SET Nombre = ?, Ciudad = ?, Pais = ?, Direccion = ?, Telefono = ? WHERE id_zoologico = ?",
                (nombre, ciudad, pais, direccion, telefono, id)
            )
            conn.commit()
            flash('Zoológico actualizado con éxito.', 'success')
            return redirect(url_for('admin.list_zoologicos'))
        except Exception as e:
            flash(f'Error al actualizar el zoológico: {e}', 'error')

    return render_template('admin/zoo_form.html', zoo=zoo)

@bp.route('/zoologicos/<string:id>/eliminar', methods=['POST'])
def delete_zoologico(id):
    """Elimina un zoológico."""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Zoologico.Zoologico WHERE id_zoologico = ?", (id,))
        conn.commit()
        flash('Zoológico eliminado con éxito.', 'success')
    except Exception as e:
        flash(f'Error al eliminar el zoológico: {e}. Es posible que tenga boletos asociados.', 'error')
    
    return redirect(url_for('admin.list_zoologicos'))
