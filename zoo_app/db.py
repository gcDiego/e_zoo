import pyodbc
from flask import current_app, g

def get_db():
    """
    Abre una nueva conexión a la base de datos si no existe una para la solicitud actual.
    """
    if 'db' not in g:
        connection_string = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=127.0.0.1,1433;"
            "DATABASE=Zoologico;"
            "UID=sa;"
            "PWD=TuPasswordSeguro123!;"
            "TrustServerCertificate=yes;"
        )
        g.db = pyodbc.connect(connection_string)
    return g.db

def close_db(e=None):
    """
    Cierra la conexión a la base de datos al final de la solicitud.
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_app(app):
    """
    Registra los comandos de la base de datos y el teardown con la aplicación.
    """
    app.teardown_appcontext(close_db)
