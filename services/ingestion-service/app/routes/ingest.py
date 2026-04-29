from flask import Blueprint, request, jsonify
from app.db import db
from app.models import Machine, Event
from app.config import Config
from datetime import datetime

ingest_bp = Blueprint("ingest", __name__)

@ingest_bp.route("/ingest", methods=["POST"])
def ingest_data():
    """
    Endpoint for Node-RED / Raspberry Pi to push real-time event data.
    X-API-KEY header is required for security.
    Payload schema:
    {
        "machine_id": "uuid",
        "event_type": "piece_detected" | "state_change" | "sensor_reading",
        "timestamp": "ISO8601 string" (optional, defaults to now),
        "metadata": { ... }
    }
    """
    if request.headers.get("X-API-KEY") != Config.API_KEY:
        return jsonify({"error": "Unauthorized: Invalid API Key"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    machine_id = data.get("machine_id")
    event_type = data.get("event_type")
    event_metadata = data.get("metadata", {})
    timestamp_str = data.get("timestamp")

    if not machine_id or not event_type:
        return jsonify({"error": "Missing machine_id or event_type"}), 400

    # Handle legacy 'm1' from simulation
    if machine_id == "m1":
        machine = Machine.query.first()
        if not machine:
            return jsonify({"error": "No machines configured in database"}), 404
        machine_id = str(machine.id)
    else:
        try:
            machine = db.session.get(Machine, machine_id)
        except Exception:
            machine = None

    if not machine:
        return jsonify({"error": "Machine not found"}), 404

    # Parse timestamp or use current time
    if timestamp_str:
        try:
            event_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            # remove tzinfo so it can be saved in naive timestamp column usually used by SQLAlchemy
            event_timestamp = event_timestamp.replace(tzinfo=None)
        except ValueError:
            event_timestamp = datetime.utcnow()
    else:
        event_timestamp = datetime.utcnow()

    # Create event
    event = Event(
        machine_id=machine.id,
        event_type=event_type,
        timestamp=event_timestamp,
        event_metadata=event_metadata
    )
    
    db.session.add(event)
    
    # Update machine status immediately for responsiveness
    if event_type == "state_change":
        new_status = event_metadata.get("state")
        if new_status:
            machine.status = new_status
    elif event_type in ["piece_detected", "sensor_reading"]:
        machine.status = "online"

    db.session.commit()
    
    return jsonify({"status": "ok", "event_id": str(event.id)}), 201
