from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from app.db import db_session
from app.helpers import require_login
from shared.models.factory import Factory
from shared.models.machine import Machine
from shared.models.kpi_snapshot import KpiSnapshot
from sqlalchemy import desc

api_bp = Blueprint("api", __name__, url_prefix="/api")

# --- Helpers ---

def get_latest_kpis(machine_id):
    """Fetch the most recent KPI snapshot for a machine."""
    latest = db_session.query(KpiSnapshot).filter_by(machine_id=machine_id).order_by(desc(KpiSnapshot.recorded_at)).first()
    if latest:
        return {
            "trs": latest.trs,
            "tdo": latest.tdo,
            "tp": latest.tp,
            "tq": latest.tq
        }
    return {"trs": 0.0, "tdo": 0.0, "tp": 0.0, "tq": 0.0}

# --- Dashboard Data ---

@api_bp.route("/dashboard-data")
@require_login
def dashboard_data():
    from app.helpers import get_current_client
    client = get_current_client()
    
    factories_data = []
    all_machines = []
    total_trs = []
    alerts = 0

    for f in client.factories:
        machines = []
        for m in f.machines:
            kpis = get_latest_kpis(m.id)
            total_trs.append(kpis["trs"])
            if kpis["trs"] < 70:
                alerts += 1
                
            machine_dict = {
                "id": str(m.id), 
                "nom": m.name, 
                "status": m.status,
                "cadence_theorique": m.theoretical_speed,
                "cycle_theorique": m.theoretical_cycle_time,
                "trs": kpis["trs"], 
                "tdo": kpis["tdo"], 
                "tp": kpis["tp"], 
                "tq": kpis["tq"],
                "seuil_vibration": m.vibration_threshold,
                "seuil_piece_cm": m.piece_cm_threshold,
                "delai_mesures": m.measurement_delays
            }
            machines.append(machine_dict)
            all_machines.append(machine_dict)
            
        factories_data.append({
            "id": str(f.id), 
            "nom": f.name, 
            "ville": f.town,
            "pays": f.country, 
            "tr": f.required_time, 
            "postes": f.positions,
            "machines": machines,
        })

    avg_trs = round(sum(total_trs) / len(total_trs), 1) if total_trs else 0

    return jsonify({
        "kpis": {
            "trs_moyen": avg_trs,
            "usines_count": len(client.factories),
            "machines_count": len(all_machines),
            "alerts": alerts,
        },
        "usines": factories_data, # Keeping 'usines' key for JS compatibility
        "machines": all_machines,
    })

# --- Factory CRUD ---

@api_bp.route("/usines", methods=["GET"]) # Keeping /usines for JS compatibility
@require_login
def get_factories():
    from app.helpers import get_current_client
    client = get_current_client()
    
    result = []
    for f in client.factories:
        result.append({
            "id": str(f.id), 
            "nom": f.name, 
            "ville": f.town,
            "pays": f.country, 
            "tr": f.required_time, 
            "postes": f.positions,
            "machines_count": len(f.machines),
            "machines": [{
                "id": str(m.id), 
                "nom": m.name,
                "cadence_theorique": m.theoretical_speed,
                "cycle_theorique": m.theoretical_cycle_time,
                "trs": get_latest_kpis(m.id)["trs"], 
                "status": m.status,
                "seuil_vibration": m.vibration_threshold,
                "seuil_piece_cm": m.piece_cm_threshold,
                "delai_mesures": m.measurement_delays
            } for m in f.machines],
        })
    return jsonify(result)

@api_bp.route("/usines", methods=["POST"])
@require_login
def add_factory():
    from app.helpers import get_current_client
    client = get_current_client()
    data = request.get_json()
    
    factory = Factory(
        client_id=client.id,
        name=data.get("nom", "Nouvelle usine"),
        town=data.get("ville", ""),
        country=data.get("pays", "Tunisie"),
        required_time=int(data.get("tr", 8)),
        positions=int(data.get("postes", 1)),
    )
    db_session.add(factory)
    db_session.commit()
    return jsonify({"status": "ok", "id": str(factory.id)})

@api_bp.route("/usines/<uuid:factory_id>", methods=["PUT"])
@require_login
def update_factory(factory_id):
    from app.helpers import get_current_client
    client = get_current_client()
    
    factory = db_session.query(Factory).filter_by(id=factory_id, client_id=client.id).first()
    if not factory:
        return jsonify({"error": "Not found"}), 404
        
    data = request.get_json()
    factory.name = data.get("nom", factory.name)
    factory.town = data.get("ville", factory.town)
    factory.country = data.get("pays", factory.country)
    factory.required_time = int(data.get("tr", factory.required_time))
    factory.positions = int(data.get("postes", factory.positions))
    
    db_session.commit()
    return jsonify({"status": "ok"})

@api_bp.route("/usines/<uuid:factory_id>", methods=["DELETE"])
@require_login
def delete_factory(factory_id):
    from app.helpers import get_current_client
    client = get_current_client()
    
    factory = db_session.query(Factory).filter_by(id=factory_id, client_id=client.id).first()
    if not factory:
        return jsonify({"error": "Not found"}), 404
        
    db_session.delete(factory)
    db_session.commit()
    return jsonify({"status": "ok"})

# --- Machine CRUD ---

@api_bp.route("/usines/<uuid:factory_id>/machines", methods=["POST"])
@require_login
def add_machine(factory_id):
    from app.helpers import get_current_client
    client = get_current_client()
    
    factory = db_session.query(Factory).filter_by(id=factory_id, client_id=client.id).first()
    if not factory:
        return jsonify({"error": "Factory not found"}), 404
        
    data = request.get_json()
    machine = Machine(
        factory_id=factory.id,
        name=data.get("nom", "Nouvelle machine"),
        theoretical_speed=float(data.get("cadence_theorique", 50)),
        theoretical_cycle_time=float(data.get("cycle_theorique", 0.0)),
        status="offline",
        vibration_threshold=float(data.get("seuil_vibration", 0.0)),
        piece_cm_threshold=float(data.get("seuil_piece_cm", 0.0)),
        measurement_delays=int(data.get("delai_mesures", 60))
    )
    db_session.add(machine)
    db_session.commit()
    return jsonify({"status": "ok", "id": str(machine.id)})

@api_bp.route("/machines/<uuid:machine_id>", methods=["PUT"])
@require_login
def update_machine(machine_id):
    from app.helpers import get_current_client
    client = get_current_client()
    
    machine = db_session.query(Machine).join(Factory).filter(
        Machine.id == machine_id, Factory.client_id == client.id
    ).first()
    
    if not machine:
        return jsonify({"error": "Not found"}), 404
        
    data = request.get_json()
    machine.name = data.get("nom", machine.name)
    machine.theoretical_speed = float(data.get("cadence_theorique", machine.theoretical_speed))
    machine.theoretical_cycle_time = float(data.get("cycle_theorique", machine.theoretical_cycle_time))
    machine.vibration_threshold = float(data.get("seuil_vibration", machine.vibration_threshold))
    machine.piece_cm_threshold = float(data.get("seuil_piece_cm", machine.piece_cm_threshold))
    machine.measurement_delays = int(data.get("delai_mesures", machine.measurement_delays))
    
    db_session.commit()
    return jsonify({"status": "ok"})

@api_bp.route("/machines/<uuid:machine_id>", methods=["DELETE"])
@require_login
def delete_machine(machine_id):
    from app.helpers import get_current_client
    client = get_current_client()
    
    machine = db_session.query(Machine).join(Factory).filter(
        Machine.id == machine_id, Factory.client_id == client.id
    ).first()
    
    if not machine:
        return jsonify({"error": "Not found"}), 404
        
    db_session.delete(machine)
    db_session.commit()
    return jsonify({"status": "ok"})

@api_bp.route("/machines/<uuid:machine_id>/details")
@require_login
def machine_details(machine_id):
    from app.helpers import get_current_client
    client = get_current_client()
    
    machine = db_session.query(Machine).join(Factory).filter(
        Machine.id == machine_id, Factory.client_id == client.id
    ).first()
    
    if not machine:
        return jsonify({"error": "Not found"}), 404
        
    kpis = get_latest_kpis(machine.id)
    
    # Mock live data for fields expected by machine.js
    import random
    mock_details = {
        "pieces_ok": random.randint(1000, 2500),
        "pieces_rebus": random.randint(5, 50),
        "cycle_time": round(60 / machine.theoretical_speed, 2) if machine.theoretical_speed > 0 else 0,
        "temperature": round(random.uniform(40.0, 75.0), 1),
        "vibration": round(random.uniform(0.5, 2.5), 2),
        "sensor_health": "Optimal" if machine.status == "online" else "Warning"
    }

    return jsonify({
        "id": str(machine.id),
        "nom": machine.name,
        "usine_nom": machine.factory.name,
        "status": machine.status,
        "cadence_theorique": machine.theoretical_speed,
        "cycle_theorique": machine.theoretical_cycle_time,
        "trs": kpis["trs"],
        "tdo": kpis["tdo"],
        "tp": kpis["tp"],
        "tq": kpis["tq"],
        "mock_live_data": mock_details
    })

# --- History ---

@api_bp.route("/machines/<uuid:machine_id>/history")
@require_login
def machine_history(machine_id):
    from app.helpers import get_current_client
    client = get_current_client()
    
    machine = db_session.query(Machine).join(Factory).filter(
        Machine.id == machine_id, Factory.client_id == client.id
    ).first()
    
    if not machine:
        return jsonify({"error": "Not found"}), 404

    days = request.args.get("days", 30, type=int)
    since = datetime.utcnow() - timedelta(days=days)

    records = db_session.query(KpiSnapshot).filter(
        KpiSnapshot.machine_id == machine_id,
        KpiSnapshot.recorded_at >= since,
    ).order_by(KpiSnapshot.recorded_at).all()

    return jsonify({
        "machine_nom": machine.name,
        "data": [{
            "date": r.recorded_at.strftime("%Y-%m-%d"),
            "trs": r.trs, "tdo": r.tdo, "tp": r.tp, "tq": r.tq,
        } for r in records],
    })

@api_bp.route("/all-machines-history")
@require_login
def all_machines_history():
    from app.helpers import get_current_client
    client = get_current_client()
    
    days = request.args.get("days", 30, type=int)
    since = datetime.utcnow() - timedelta(days=days)
    result = []
    
    for f in client.factories:
        for m in f.machines:
            records = db_session.query(KpiSnapshot).filter(
                KpiSnapshot.machine_id == m.id,
                KpiSnapshot.recorded_at >= since,
            ).order_by(KpiSnapshot.recorded_at).all()
            
            result.append({
                "machine_id": str(m.id),
                "machine_nom": m.name,
                "usine_nom": f.name,
                "data": [{
                    "date": r.recorded_at.strftime("%Y-%m-%d"),
                    "trs": r.trs, "tdo": r.tdo, "tp": r.tp, "tq": r.tq,
                } for r in records],
            })
    return jsonify(result)

# --- Profile ---

@api_bp.route("/profile", methods=["PUT"])
@require_login
def update_profile():
    from app.helpers import get_current_client
    client = get_current_client()
    data = request.get_json()
    
    client.firstname = data.get("prenom", client.firstname)
    client.lastname = data.get("nom", client.lastname)
    client.phone_number = data.get("telephone", client.phone_number)
    client.entreprise = data.get("entreprise", client.entreprise)
    client.sector = data.get("secteur", client.sector)
    
    if data.get("new_password"):
        if data.get("current_password") == client.password:
            client.password = data["new_password"]
        else:
            return jsonify({"error": "Mot de passe actuel incorrect"}), 400
            
    db_session.commit()
    return jsonify({"status": "ok"})
