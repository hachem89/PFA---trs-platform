from flask import Blueprint, render_template, abort
from app.helpers import require_login, get_current_client
from app.db import db_session
from shared.models.machine import Machine

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/dashboard")
@require_login
def dashboard():
    client = get_current_client()
    return render_template("dashboard.html", client=client, page="dashboard")

@pages_bp.route("/analysis")
@require_login
def analysis():
    client = get_current_client()
    return render_template("analysis.html", client=client, page="analysis")

@pages_bp.route("/settings")
@require_login
def settings():
    client = get_current_client()
    return render_template("settings.html", client=client, page="settings")

@pages_bp.route("/profile")
@require_login
def profile():
    client = get_current_client()
    return render_template("profile.html", client=client, page="profile")

@pages_bp.route("/machine/<uuid:machine_id>")
@require_login
def machine(machine_id):
    client = get_current_client()
    
    # Check if the machine exists and belongs to the client
    # This ensures security (one client can't see another client's machine)
    machine_record = db_session.query(Machine).filter(
        Machine.id == machine_id
    ).first()
    
    if not machine_record:
        abort(404)
        
    return render_template("machine.html", client=client, machine_id=str(machine_id), page="dashboard")
