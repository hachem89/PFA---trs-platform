from flask import Flask
from app.db import db_session
from app.routes.auth import auth_bp
from app.routes.pages import pages_bp
from app.routes.api import api_bp
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)

    # Teardown database session after each request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    return app
