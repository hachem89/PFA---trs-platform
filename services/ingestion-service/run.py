import shared.models   
from flask import Flask
from app.routes.ingest import ingest_bp
import threading
import time
from app.services.cleanup import cleanup_old_events

def start_cleanup_worker():
    def run_periodically():
        while True:
            # We wait a bit on startup to let the DB settle
            time.sleep(60) 
            cleanup_old_events(days=3)
            # Run every 12 hours
            time.sleep(3600 * 12) 
            
    thread = threading.Thread(target=run_periodically, daemon=True)
    thread.start()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(ingest_bp)
    
    # Start the background worker
    start_cleanup_worker()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)