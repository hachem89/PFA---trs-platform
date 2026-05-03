from flask import Flask
from app.db import db
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Import and register blueprints
    from app.kpi_engine import kpi_engine_bp
    app.register_blueprint(kpi_engine_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(port=5002, debug=True)