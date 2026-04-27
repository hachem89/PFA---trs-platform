from flask import Flask
from app.db import db
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # register routes
    from app.routes.ingest import ingest_bp
    app.register_blueprint(ingest_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5001, debug=True)