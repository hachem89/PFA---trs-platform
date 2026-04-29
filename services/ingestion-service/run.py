from flask import Flask
from app.routes.ingest import ingest_bp
import shared.models   

def create_app():
    app = Flask(__name__)

    app.register_blueprint(ingest_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)