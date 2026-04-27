from flask import Blueprint, jsonify, request
from datetime import datetime
from app.config import Config
from app.db import db
from shared.models.kpi_snapshot import KpiSnapshot
from shared.models.machine import Machine

# ── Blueprint ──────────────────────────────────────────────
ingest_bp = Blueprint("ingest", __name__)

# ── IoT Ingestion (Node-RED / Raspberry Pi) ───────────────

@ingest_bp.route("/ingest/machine/<int:machine_id>", methods=["POST"])
def ingest_machine_data(machine_id):
    """
    Endpoint for Raspberry Pi / Node-RED to push real-time data.
    X-API-KEY header is required for security.
    """
    # 1. Security Check
    if request.headers.get("X-API-KEY") != Config.API_KEY:
        return jsonify({"error": "Unauthorized: Invalid API Key"}), 403

    # 2. Get Machine
    machine = db.session.get(Machine, machine_id)
    if not machine:
        return jsonify({"error": "Machine not found"}), 404

    # 3. Parse and Update Current State
    data = request.get_json()
    machine.trs = data.get("trs", machine.trs)
    machine.tdo = data.get("tdo", machine.tdo)
    machine.tp = data.get("tp", machine.tp)
    machine.tq = data.get("tq", machine.tq)
    machine.status = data.get("status", "online")

    # 4. Hourly Snapshot Logic
    # We only save a history record if the last one was more than 1 hour ago
    last_record = KpiSnapshot.query.filter_by(machine_id=machine.id).order_by(KpiSnapshot.recorded_at.desc()).first()
    now = datetime.utcnow()

    if not last_record or (now - last_record.recorded_at).total_seconds() >= 3600:
        new_history = KpiSnapshot(
            machine_id=machine.id,
            trs=machine.trs,
            tdo=machine.tdo,
            tp=machine.tp,
            tq=machine.tq,
            recorded_at=now
        )
        db.session.add(new_history)

    db.session.commit()
    return jsonify({"status": "ok"})

