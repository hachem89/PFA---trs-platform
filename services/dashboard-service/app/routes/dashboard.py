from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request
from app.db import db
from app.models import Factory, Machine, KpiSnapshot
from app.helpers import require_login

dashboard_bp = Blueprint("dashboard", __name__)

# ── Pages ───────────────────────────────────────────────────

@dashboard_bp.route("/dashboard")
@require_login
def dashboard(client):
    return render_template("dashboard.html", client=client, page="dashboard")

@dashboard_bp.route("/analysis")
@require_login
def analysis(client):
    return render_template("analysis.html", client=client, page="analysis")

@dashboard_bp.route("/settings")
@require_login
def settings(client):
    return render_template("settings.html", client=client, page="settings")

@dashboard_bp.route("/profile")
@require_login
def profile(client):
    return render_template("profile.html", client=client, page="profile")

@dashboard_bp.route("/machine/<uuid:machine_id>")
@require_login
def machine(client, machine_id):
    machine_record = Machine.query.get_or_404(machine_id)
    return render_template("machine.html", client=client, machine_id=str(machine_id), page="machine")

# ── API Routes ──────────────────────────────────────────────

@dashboard_bp.route("/api/dashboard-data")
@require_login
def dashboard_data(client):
    factories_data = []
    all_machines = []
    total_trs = []
    alerts = 0

    for f in client.factories:
        machines = []
        for m in f.machines:
            total_trs.append(m.trs)
            if m.trs < 70:
                alerts += 1
            machines.append({
                "id": str(m.id), "name": m.name, "status": m.status,
                "theoretical_speed": m.theoretical_speed,
                "trs": m.trs, "tdo": m.tdo, "tp": m.tp, "tq": m.tq,
            })
            all_machines.append(machines[-1])
        factories_data.append({
            "id": str(f.id), "name": f.name, "town": f.town,
            "country": f.country, "required_time": f.required_time, "positions": f.positions,
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
        "usines": factories_data,
        "machines": all_machines,
    })

@dashboard_bp.route("/api/usines", methods=["GET"])
@require_login
def get_factories(client):
    result = []
    for f in client.factories:
        result.append({
            "id": str(f.id), "nom": f.name, "ville": f.town,
            "pays": f.country, "tr": f.required_time, "postes": f.positions,
            "machines_count": len(f.machines),
            "machines": [{
                "id": str(m.id), "nom": m.name,
                "cadence_theorique": m.theoretical_speed,
                "trs": m.trs, "status": m.status,
            } for m in f.machines],
        })
    return jsonify(result)

@dashboard_bp.route("/api/usines", methods=["POST"])
@require_login
def add_factory(client):
    data = request.get_json()
    factory = Factory(
        client_id=client.id,
        name=data.get("nom", "New Factory"),
        town=data.get("ville", ""),
        country=data.get("pays", "Tunisia"),
        required_time=int(data.get("tr", 8)),
        positions=int(data.get("postes", 1)),
    )
    db.session.add(factory)
    db.session.commit()
    return jsonify({"status": "ok", "id": str(factory.id)})

@dashboard_bp.route("/api/usines/<uuid:factory_id>", methods=["PUT"])
@require_login
def update_factory(client, factory_id):
    factory = Factory.query.filter_by(id=factory_id, client_id=client.id).first()
    if not factory:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    factory.name = data.get("nom", factory.name)
    factory.town = data.get("ville", factory.town)
    factory.country = data.get("pays", factory.country)
    factory.required_time = int(data.get("tr", factory.required_time))
    factory.positions = int(data.get("postes", factory.positions))
    db.session.commit()
    return jsonify({"status": "ok"})

@dashboard_bp.route("/api/usines/<uuid:factory_id>", methods=["DELETE"])
@require_login
def delete_factory(client, factory_id):
    factory = Factory.query.filter_by(id=factory_id, client_id=client.id).first()
    if not factory:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(factory)
    db.session.commit()
    return jsonify({"status": "ok"})

@dashboard_bp.route("/api/usines/<uuid:factory_id>/machines", methods=["POST"])
@require_login
def add_machine(client, factory_id):
    factory = Factory.query.filter_by(id=factory_id, client_id=client.id).first()
    if not factory:
        return jsonify({"error": "Factory not found"}), 404
    data = request.get_json()
    machine = Machine(
        factory_id=factory.id,
        name=data.get("nom", "New Machine"),
        theoretical_speed=float(data.get("cadence_theorique", 50)),
        status="offline",
        vibration_threshold=float(data.get("seuil_vibration", 0.0)),
        piece_cm_threshold=float(data.get("seuil_piece_cm", 0.0)),
        measurement_delays=int(data.get("delai_mesures", 60)),
    )
    db.session.add(machine)
    db.session.commit()
    return jsonify({"status": "ok", "id": str(machine.id)})

@dashboard_bp.route("/api/machines/<uuid:machine_id>", methods=["PUT"])
@require_login
def update_machine(client, machine_id):
    machine = Machine.query.join(Factory).filter(
        Machine.id == machine_id, Factory.client_id == client.id
    ).first()
    if not machine:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    machine.name = data.get("nom", machine.name)
    machine.theoretical_speed = float(data.get("cadence_theorique", machine.theoretical_speed))
    machine.vibration_threshold = float(data.get("seuil_vibration", machine.vibration_threshold))
    machine.piece_cm_threshold = float(data.get("seuil_piece_cm", machine.piece_cm_threshold))
    machine.measurement_delays = int(data.get("delai_mesures", machine.measurement_delays))
    db.session.commit()
    return jsonify({"status": "ok"})

@dashboard_bp.route("/api/machines/<uuid:machine_id>", methods=["DELETE"])
@require_login
def delete_machine(client, machine_id):
    machine = Machine.query.join(Factory).filter(
        Machine.id == machine_id, Factory.client_id == client.id
    ).first()
    if not machine:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(machine)
    db.session.commit()
    return jsonify({"status": "ok"})

@dashboard_bp.route("/api/machines/<uuid:machine_id>/details")
@require_login
def machine_details(client, machine_id):
    machine = Machine.query.join(Factory).filter(
        Machine.id == machine_id, Factory.client_id == client.id
    ).first()
    
    if not machine:
        return jsonify({"error": "Not found"}), 404
        
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
        "trs": machine.trs,
        "tdo": machine.tdo,
        "tp": machine.tp,
        "tq": machine.tq,
        "mock_live_data": mock_details
    })

@dashboard_bp.route("/api/machines/<uuid:machine_id>/history")
@require_login
def machine_history(client, machine_id):
    machine = Machine.query.join(Factory).filter(
        Machine.id == machine_id, Factory.client_id == client.id
    ).first()
    if not machine:
        return jsonify({"error": "Not found"}), 404

    days = request.args.get("days", 30, type=int)
    since = datetime.utcnow() - timedelta(days=days)

    records = KpiSnapshot.query.filter(
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

@dashboard_bp.route("/api/all-machines-history")
@require_login
def all_machines_history(client):
    days = request.args.get("days", 30, type=int)
    since = datetime.utcnow() - timedelta(days=days)
    result = []
    for f in client.factories:
        for m in f.machines:
            records = KpiSnapshot.query.filter(
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

@dashboard_bp.route("/api/profile", methods=["PUT"])
@require_login
def update_profile(client):
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
            return jsonify({"error": "Incorrect current password"}), 400
    db.session.commit()
    return jsonify({"status": "ok"})
