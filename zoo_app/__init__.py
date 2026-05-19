import os
from flask import Flask
from dotenv import load_dotenv
from flask_mail import Mail

mail = Mail()

def create_app():
    """Crea y configura una instancia de la aplicación Flask."""
    load_dotenv()
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder='../templates',
        static_folder='../static'
    )
    
    # Configuración general y de la base de datos
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
    )

    # Configuración de Flask-Mail desde variables de entorno
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')

    # Inicializar extensiones
    from . import db
    db.init_app(app)
    mail.init_app(app)

    # Registrar los Blueprints
    from . import main_routes, admin_routes, api_routes
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(admin_routes.bp)
    app.register_blueprint(api_routes.bp)

    # Asegurarse de que las rutas de los Blueprints están disponibles
    app.add_url_rule('/', endpoint='index')

    return app
