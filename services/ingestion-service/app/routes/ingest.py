from flask import Blueprint, request, jsonify
from app.services.event_service import create_event
from app.config import Config

ingest_bp = Blueprint("ingest", __name__)

@ingest_bp.route("/events/ingest", methods=["POST"])
def ingest_event():

    # 🔐 API protection
    if request.headers.get("x-api-key") != Config.API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()

    if not data or not data.get("event_type"):
        return jsonify({"error": "Invalid event"}), 400

    try:
        event = create_event(data)

        return jsonify({
            "message": "Event stored",
            "event_id": str(event.id)
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500