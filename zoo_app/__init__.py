import os
from flask import Flask
from dotenv import load_dotenv

def create_app():
    """Crea y configura una instancia de la aplicación Flask."""
    load_dotenv()
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder='../templates',
        static_folder='../static'
    )
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
    )

    # Registrar la gestión de la base de datos
    from . import db
    db.init_app(app)

    # Registrar los Blueprints
    from . import main_routes, admin_routes, api_routes
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(admin_routes.bp)
    app.register_blueprint(api_routes.bp)

    # Asegurarse de que las rutas de los Blueprints están disponibles
    app.add_url_rule('/', endpoint='index')

    return app
