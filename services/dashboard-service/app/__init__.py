from flask import Flask, render_template
from app.db import db_session
from app.routes.auth import auth_bp
from app.helpers import require_login, get_current_client
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register the Authentication Blueprint
    app.register_blueprint(auth_bp)

    # Teardown database session after each request
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    # --- Page Routes (Will be moved to routes/pages.py in Phase 3) ---

    @app.route('/dashboard')
    @require_login
    def dashboard():
        client = get_current_client()
        return render_template('dashboard.html', client=client, page='dashboard')

    @app.route('/analysis')
    @require_login
    def analysis():
        client = get_current_client()
        return render_template('analysis.html', client=client, page='analysis')

    @app.route('/settings')
    @require_login
    def settings():
        client = get_current_client()
        return render_template('settings.html', client=client, page='settings')

    @app.route('/profile')
    @require_login
    def profile():
        client = get_current_client()
        return render_template('profile.html', client=client, page='profile')
        
    @app.route('/machine/<uuid:machine_id>') # Use uuid converter for PostgreSQL IDs
    @require_login
    def machine(machine_id):
        client = get_current_client()
        return render_template('machine.html', client=client, page='dashboard', machine_id=str(machine_id))

    return app
