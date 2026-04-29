# Project Tree Structure

```text
trs_digitalisation/
├── .env
├── .env.example
├── .gitignore
├── app.py
├── ARCHITECTURE.md
├── config.py
├── extensions.py
├── helpers.py
├── migrate_db.py
├── models.py
├── routes/
│   ├── __init__.py
│   ├── api.py
│   ├── auth.py
│   └── pages.py
├── static/
│   ├── css/
│   │   ├── analysis.css
│   │   ├── base.css
│   │   ├── dashboard.css
│   │   ├── machine.css
│   │   ├── profile.css
│   │   └── settings.css
│   └── js/
│       ├── analysis.js
│       ├── base.js
│       ├── dashboard.js
│       ├── machine.js
│       ├── profile.js
│       └── settings.js
└── templates/
    ├── analysis.html
    ├── base.html
    ├── dashboard.html
    ├── login.html
    ├── machine.html
    ├── profile.html
    ├── settings.html
    └── usine.html
```

---

# Python Files (Backend Code)

### `app.py`
**Description:** Application entry point. Responsible for creating the Flask app, registering blueprints, initializing extensions (database), and creating tables.

```python
"""
Application entry point.
Single Responsibility: Only creates the Flask app, registers blueprints,
and initialises the database. No business logic lives here.
"""

from flask import Flask

from config import Config
from extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialise extensions
    db.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.pages import pages_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(pages_bp)
    app.register_blueprint(api_bp)

    # Create tables
    with app.app_context():
        from models import Client, Usine, Machine, TrsHistory  # noqa: F401
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
```

### `config.py`
**Description:** Handles application configuration, pulling environment variables like the secret key, database URL, and API key.

```python
"""
Application configuration.
Single Responsibility: Only handles configuration values.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback_secret_if_not_found")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    API_KEY = os.environ.get("API_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### `extensions.py`
**Description:** Sets up Flask extensions such as SQLAlchemy. Extracted to avoid circular imports between models and routes.

```python
"""
Flask extensions (SQLAlchemy).
Separated to avoid circular imports between models and routes.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

### `helpers.py`
**Description:** Contains shared helper functions, including authentication decorators (`@require_login`) and the demo data seeding script for new machines (`seed_demo_history`).

```python
"""
Shared helpers: authentication decorator and demo data seeder.
Single Responsibility: Utility functions used across multiple route modules.
"""

import random
from datetime import datetime, timedelta
from functools import wraps

from flask import redirect, session

from extensions import db
from models import Client, TrsHistory


def get_current_client():
    """Return the logged-in Client or None."""
    if "client_id" not in session:
        return None
    return db.session.get(Client, session["client_id"])


def require_login(f):
    """Decorator — redirects to /login if not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        client = get_current_client()
        if not client:
            return redirect("/login")
        return f(client, *args, **kwargs)
    return decorated


def seed_demo_history(machine):
    """Generate 30 days of simulated TRS history for a machine."""
    now = datetime.utcnow()
    for i in range(30):
        day = now - timedelta(days=29 - i)
        base_trs = random.uniform(60, 95)
        base_tdo = random.uniform(75, 98)
        base_tp = random.uniform(65, 95)
        base_tq = random.uniform(85, 99)
        record = TrsHistory(
            machine_id=machine.id,
            trs=round(base_trs, 1),
            tdo=round(base_tdo, 1),
            tp=round(base_tp, 1),
            tq=round(base_tq, 1),
            recorded_at=day,
        )
        db.session.add(record)
    # Update machine current values with the latest
    machine.trs = round(base_trs, 1)
    machine.tdo = round(base_tdo, 1)
    machine.tp = round(base_tp, 1)
    machine.tq = round(base_tq, 1)
    machine.status = "online"
```

### `migrate_db.py`
**Description:** Standalone script for running simple manual SQL migrations to extend the database schema without using Flask-Migrate (e.g., adding machine configuration parameters).

```python
import psycopg2
from config import Config

def migrate():
    # Extract DB URL from config or hardcode the default for this run
    db_url = Config.SQLALCHEMY_DATABASE_URI
    
    if not db_url:
        print("DATABASE_URL not found in environment")
        return
        
    try:
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Add the columns if they don't exist
        print("Adding seuil_vibration...")
        cur.execute("ALTER TABLE machines ADD COLUMN IF NOT EXISTS seuil_vibration FLOAT DEFAULT 0.0;")
        
        print("Adding seuil_piece_cm...")
        cur.execute("ALTER TABLE machines ADD COLUMN IF NOT EXISTS seuil_piece_cm FLOAT DEFAULT 0.0;")
        
        print("Adding delai_mesures...")
        cur.execute("ALTER TABLE machines ADD COLUMN IF NOT EXISTS delai_mesures INTEGER DEFAULT 60;")
        
        conn.commit()
        cur.close()
        conn.close()
        print("Migration successful.")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
```

### `models.py`
**Description:** Defines the database schema using SQLAlchemy models representing Users (`Client`), Factories (`Usine`), Machines (`Machine`), and Timeseries logs (`TrsHistory`).

```python
"""
Database models.
Single Responsibility: Each model class represents one database table.
"""

from datetime import datetime
from extensions import db


class Client(db.Model):
    """User account — represents a factory owner."""
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    prenom = db.Column(db.String(100))
    nom = db.Column(db.String(100))
    entreprise = db.Column(db.String(200))
    telephone = db.Column(db.String(20))
    secteur = db.Column(db.String(100))

    usines = db.relationship(
        "Usine", backref="client", lazy=True, cascade="all, delete-orphan"
    )


class Usine(db.Model):
    """Factory / production site."""
    __tablename__ = "usines"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    ville = db.Column(db.String(100))
    pays = db.Column(db.String(100))
    tr = db.Column(db.Integer, default=8)
    postes = db.Column(db.Integer, default=1)

    machines = db.relationship(
        "Machine", backref="usine", lazy=True, cascade="all, delete-orphan"
    )


class Machine(db.Model):
    """Individual machine inside a factory."""
    __tablename__ = "machines"

    id = db.Column(db.Integer, primary_key=True)
    usine_id = db.Column(db.Integer, db.ForeignKey("usines.id"), nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    cadence_theorique = db.Column(db.Float, nullable=False)
    trs = db.Column(db.Float, default=0.0)
    tdo = db.Column(db.Float, default=0.0)
    tp = db.Column(db.Float, default=0.0)
    tq = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="offline")
    
    # New configurations
    seuil_vibration = db.Column(db.Float, default=0.0)
    seuil_piece_cm = db.Column(db.Float, default=0.0)
    delai_mesures = db.Column(db.Integer, default=60) # In seconds
    
    capteur_vitesse = db.Column(db.String(50))
    capteur_pieces = db.Column(db.String(50))
    capteur_dispo = db.Column(db.String(50))
    capteur_qualite = db.Column(db.String(50))

    history = db.relationship(
        "TrsHistory", backref="machine", lazy=True, cascade="all, delete-orphan"
    )


class TrsHistory(db.Model):
    """Time-series record of TRS/TDO/TP/TQ for a machine."""
    __tablename__ = "trs_history"

    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machines.id"), nullable=False)
    trs = db.Column(db.Float, default=0.0)
    tdo = db.Column(db.Float, default=0.0)
    tp = db.Column(db.Float, default=0.0)
    tq = db.Column(db.Float, default=0.0)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### `routes/__init__.py`
**Description:** Makes the routes directory a Python package.

```python
# Routes package
```

### `routes/api.py`
**Description:** Implements JSON API endpoints for dashboard data, CRUD operations for machines and usines, IoT hardware ingestion endpoints (Raspberry Pi/Node-RED), and profile updates.

```python
"""
JSON API routes: CRUD for usines, machines, TRS history, profile.
Single Responsibility: Only handles API data endpoints.
Open/Closed: New resource endpoints can be added without modifying existing ones.
"""

from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request

from extensions import db
from models import Usine, Machine, TrsHistory
from helpers import require_login, seed_demo_history
from config import Config

api_bp = Blueprint("api", __name__, url_prefix="/api")

# ── Dashboard Data ──────────────────────────────────────────

@api_bp.route("/dashboard-data")
@require_login
def dashboard_data(client):
    usines_data = []
    all_machines = []
    total_trs = []
    alerts = 0

    for u in client.usines:
        machines = []
        for m in u.machines:
            total_trs.append(m.trs)
            if m.trs < 70:
                alerts += 1
            machines.append({
                "id": m.id, "nom": m.nom, "status": m.status,
                "cadence_theorique": m.cadence_theorique,
                "trs": m.trs, "tdo": m.tdo, "tp": m.tp, "tq": m.tq,
                "seuil_vibration": m.seuil_vibration,
                "seuil_piece_cm": m.seuil_piece_cm,
                "delai_mesures": m.delai_mesures,
                "capteur_vitesse": m.capteur_vitesse,
                "capteur_pieces": m.capteur_pieces,
                "capteur_dispo": m.capteur_dispo,
                "capteur_qualite": m.capteur_qualite,
            })
            all_machines.append(machines[-1])
        usines_data.append({
            "id": u.id, "nom": u.nom, "ville": u.ville,
            "pays": u.pays, "tr": u.tr, "postes": u.postes,
            "machines": machines,
        })

    avg_trs = round(sum(total_trs) / len(total_trs), 1) if total_trs else 0

    return jsonify({
        "kpis": {
            "trs_moyen": avg_trs,
            "usines_count": len(client.usines),
            "machines_count": len(all_machines),
            "alerts": alerts,
        },
        "usines": usines_data,
        "machines": all_machines,
    })


# ── Usine CRUD ──────────────────────────────────────────────

@api_bp.route("/usines", methods=["GET"])
@require_login
def get_usines(client):
    result = []
    for u in client.usines:
        result.append({
            "id": u.id, "nom": u.nom, "ville": u.ville,
            "pays": u.pays, "tr": u.tr, "postes": u.postes,
            "machines_count": len(u.machines),
            "machines": [{
                "id": m.id, "nom": m.nom,
                "cadence_theorique": m.cadence_theorique,
                "trs": m.trs, "status": m.status,
                "seuil_vibration": m.seuil_vibration,
                "seuil_piece_cm": m.seuil_piece_cm,
                "delai_mesures": m.delai_mesures,
                "capteur_vitesse": m.capteur_vitesse,
                "capteur_pieces": m.capteur_pieces,
                "capteur_dispo": m.capteur_dispo,
                "capteur_qualite": m.capteur_qualite,
            } for m in u.machines],
        })
    return jsonify(result)


@api_bp.route("/usines", methods=["POST"])
@require_login
def add_usine(client):
    data = request.get_json()
    usine = Usine(
        client_id=client.id,
        nom=data.get("nom", "Nouvelle usine"),
        ville=data.get("ville", ""),
        pays=data.get("pays", "Tunisie"),
        tr=int(data.get("tr", 8)),
        postes=int(data.get("postes", 1)),
    )
    db.session.add(usine)
    db.session.commit()
    return jsonify({"status": "ok", "id": usine.id})


@api_bp.route("/usines/<int:usine_id>", methods=["PUT"])
@require_login
def update_usine(client, usine_id):
    usine = Usine.query.filter_by(id=usine_id, client_id=client.id).first()
    if not usine:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    usine.nom = data.get("nom", usine.nom)
    usine.ville = data.get("ville", usine.ville)
    usine.pays = data.get("pays", usine.pays)
    usine.tr = int(data.get("tr", usine.tr))
    usine.postes = int(data.get("postes", usine.postes))
    db.session.commit()
    return jsonify({"status": "ok"})


@api_bp.route("/usines/<int:usine_id>", methods=["DELETE"])
@require_login
def delete_usine(client, usine_id):
    usine = Usine.query.filter_by(id=usine_id, client_id=client.id).first()
    if not usine:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(usine)
    db.session.commit()
    return jsonify({"status": "ok"})


# ── Machine CRUD ────────────────────────────────────────────

@api_bp.route("/usines/<int:usine_id>/machines", methods=["POST"])
@require_login
def add_machine(client, usine_id):
    usine = Usine.query.filter_by(id=usine_id, client_id=client.id).first()
    if not usine:
        return jsonify({"error": "Usine not found"}), 404
    data = request.get_json()
    machine = Machine(
        usine_id=usine.id,
        nom=data.get("nom", "Nouvelle machine"),
        cadence_theorique=float(data.get("cadence_theorique", 50)),
        status="offline",
        seuil_vibration=float(data.get("seuil_vibration", 0.0)),
        seuil_piece_cm=float(data.get("seuil_piece_cm", 0.0)),
        delai_mesures=int(data.get("delai_mesures", 60)),
        capteur_vitesse=data.get("capteur_vitesse", "simulation"),
        capteur_pieces=data.get("capteur_pieces", "simulation"),
        capteur_dispo=data.get("capteur_dispo", "simulation"),
        capteur_qualite=data.get("capteur_qualite", "simulation"),
    )
    db.session.add(machine)
    db.session.flush()
    seed_demo_history(machine)
    db.session.commit()
    return jsonify({"status": "ok", "id": machine.id})


@api_bp.route("/machines/<int:machine_id>", methods=["PUT"])
@require_login
def update_machine(client, machine_id):
    machine = Machine.query.join(Usine).filter(
        Machine.id == machine_id, Usine.client_id == client.id
    ).first()
    if not machine:
        return jsonify({"error": "Not found"}), 404
    data = request.get_json()
    machine.nom = data.get("nom", machine.nom)
    machine.cadence_theorique = float(data.get("cadence_theorique", machine.cadence_theorique))
    machine.seuil_vibration = float(data.get("seuil_vibration", machine.seuil_vibration))
    machine.seuil_piece_cm = float(data.get("seuil_piece_cm", machine.seuil_piece_cm))
    machine.delai_mesures = int(data.get("delai_mesures", machine.delai_mesures))
    machine.capteur_vitesse = data.get("capteur_vitesse", machine.capteur_vitesse)
    machine.capteur_pieces = data.get("capteur_pieces", machine.capteur_pieces)
    machine.capteur_dispo = data.get("capteur_dispo", machine.capteur_dispo)
    machine.capteur_qualite = data.get("capteur_qualite", machine.capteur_qualite)
    db.session.commit()
    return jsonify({"status": "ok"})


@api_bp.route("/machines/<int:machine_id>", methods=["DELETE"])
@require_login
def delete_machine(client, machine_id):
    machine = Machine.query.join(Usine).filter(
        Machine.id == machine_id, Usine.client_id == client.id
    ).first()
    if not machine:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(machine)
    db.session.commit()
    return jsonify({"status": "ok"})


@api_bp.route("/machines/<int:machine_id>/details")
@require_login
def machine_details(client, machine_id):
    machine = Machine.query.join(Usine).filter(
        Machine.id == machine_id, Usine.client_id == client.id
    ).first()
    
    if not machine:
        return jsonify({"error": "Not found"}), 404
        
    # Hardcoded mock data for fields expected from Node-RED later
    import random
    mock_details = {
        "pieces_ok": random.randint(1000, 2500),
        "pieces_rebus": random.randint(5, 50),
        "cycle_time": round(60 / machine.cadence_theorique, 2) if machine.cadence_theorique > 0 else 0,
        "temperature": round(random.uniform(40.0, 75.0), 1),
        "vibration": round(random.uniform(0.5, 2.5), 2),
        "sensor_health": "Optimal" if machine.status == "online" else "Warning"
    }

    return jsonify({
        "id": machine.id,
        "nom": machine.nom,
        "usine_nom": machine.usine.nom,
        "status": machine.status,
        "cadence_theorique": machine.cadence_theorique,
        "trs": machine.trs,
        "tdo": machine.tdo,
        "tp": machine.tp,
        "tq": machine.tq,
        "capteur_vitesse": machine.capteur_vitesse,
        "capteur_pieces": machine.capteur_pieces,
        "capteur_dispo": machine.capteur_dispo,
        "capteur_qualite": machine.capteur_qualite,
        "mock_live_data": mock_details
    })

# ── TRS History ─────────────────────────────────────────────

@api_bp.route("/machines/<int:machine_id>/history")
@require_login
def machine_history(client, machine_id):
    machine = Machine.query.join(Usine).filter(
        Machine.id == machine_id, Usine.client_id == client.id
    ).first()
    if not machine:
        return jsonify({"error": "Not found"}), 404

    days = request.args.get("days", 30, type=int)
    since = datetime.utcnow() - timedelta(days=days)

    records = TrsHistory.query.filter(
        TrsHistory.machine_id == machine_id,
        TrsHistory.recorded_at >= since,
    ).order_by(TrsHistory.recorded_at).all()

    return jsonify({
        "machine_nom": machine.nom,
        "data": [{
            "date": r.recorded_at.strftime("%Y-%m-%d"),
            "trs": r.trs, "tdo": r.tdo, "tp": r.tp, "tq": r.tq,
        } for r in records],
    })


@api_bp.route("/all-machines-history")
@require_login
def all_machines_history(client):
    days = request.args.get("days", 30, type=int)
    since = datetime.utcnow() - timedelta(days=days)
    result = []
    for u in client.usines:
        for m in u.machines:
            records = TrsHistory.query.filter(
                TrsHistory.machine_id == m.id,
                TrsHistory.recorded_at >= since,
            ).order_by(TrsHistory.recorded_at).all()
            result.append({
                "machine_id": m.id,
                "machine_nom": m.nom,
                "usine_nom": u.nom,
                "data": [{
                    "date": r.recorded_at.strftime("%Y-%m-%d"),
                    "trs": r.trs, "tdo": r.tdo, "tp": r.tp, "tq": r.tq,
                } for r in records],
            })
    return jsonify(result)


# ── Profile ─────────────────────────────────────────────────

@api_bp.route("/profile", methods=["PUT"])
@require_login
def update_profile(client):
    data = request.get_json()
    client.prenom = data.get("prenom", client.prenom)
    client.nom = data.get("nom", client.nom)
    client.telephone = data.get("telephone", client.telephone)
    client.entreprise = data.get("entreprise", client.entreprise)
    client.secteur = data.get("secteur", client.secteur)
    if data.get("new_password"):
        if data.get("current_password") == client.password:
            client.password = data["new_password"]
        else:
            return jsonify({"error": "Mot de passe actuel incorrect"}), 400
    db.session.commit()
    return jsonify({"status": "ok"})


# ── IoT Ingestion (Node-RED / Raspberry Pi) ───────────────

@api_bp.route("/ingest/machine/<int:machine_id>", methods=["POST"])
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
    last_record = TrsHistory.query.filter_by(machine_id=machine.id).order_by(TrsHistory.recorded_at.desc()).first()
    now = datetime.utcnow()

    if not last_record or (now - last_record.recorded_at).total_seconds() >= 3600:
        new_history = TrsHistory(
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


# ── Legacy ──────────────────────────────────────────────────

@api_bp.route("/trs", methods=["POST"])
def trs():
    data = request.get_json()
    return jsonify({"status": "OK", "received": data})
```

### `routes/auth.py`
**Description:** Handles user authentication, including login, registration (and related initial scaffolding for a new user's factory/machines), and logout.

```python
"""
Authentication routes: login, register, logout.
Single Responsibility: Only handles auth-related endpoints.
"""

from flask import Blueprint, render_template, request, redirect, session

from extensions import db
from models import Client, Usine, Machine
from helpers import seed_demo_history

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    return redirect("/login")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        client = Client.query.filter_by(email=email).first()
        if client and client.password == password:
            session["client_id"] = client.id
            return redirect("/dashboard")
        return render_template("login.html", error="Email ou mot de passe incorrect")
    return render_template("login.html")


@auth_bp.route("/register", methods=["POST"])
def register():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()
    prenom = request.form.get("prenom", "")
    nom = request.form.get("nom", "")
    entreprise = request.form.get("entreprise", "")
    telephone = request.form.get("telephone", "")
    secteur = request.form.get("secteur", "")

    if Client.query.filter_by(email=email).first():
        return render_template("login.html", error="Cet email est déjà utilisé")

    new_client = Client(
        email=email, password=password, prenom=prenom, nom=nom,
        entreprise=entreprise, telephone=telephone, secteur=secteur,
    )
    db.session.add(new_client)
    db.session.flush()

    new_usine = Usine(
        client_id=new_client.id,
        nom=request.form.get("usine_nom", "Usine principale"),
        ville=request.form.get("usine_ville", ""),
        pays=request.form.get("usine_pays", "Tunisie"),
        tr=int(request.form.get("usine_tr", 8)),
        postes=int(request.form.get("usine_postes", 1)),
    )
    db.session.add(new_usine)
    db.session.flush()

    i = 0
    while request.form.get(f"machine_nom_{i}"):
        new_machine = Machine(
            usine_id=new_usine.id,
            nom=request.form.get(f"machine_nom_{i}"),
            cadence_theorique=float(request.form.get(f"machine_cadence_{i}", 50)),
            trs=0, tdo=0, tp=0, tq=0,
            status="offline",
            seuil_vibration=float(request.form.get(f"machine_seuil_vibration_{i}", 0.0)),
            seuil_piece_cm=float(request.form.get(f"machine_seuil_piece_cm_{i}", 0.0)),
            delai_mesures=int(request.form.get(f"machine_delai_{i}", 60)),
            capteur_vitesse=request.form.get(f"machine_capteur_vitesse_{i}", "simulation"),
            capteur_pieces=request.form.get(f"machine_capteur_pieces_{i}", "simulation"),
            capteur_dispo=request.form.get(f"machine_capteur_dispo_{i}", "simulation"),
            capteur_qualite=request.form.get(f"machine_capteur_qualite_{i}", "simulation"),
        )
        db.session.add(new_machine)
        db.session.flush()
        seed_demo_history(new_machine)
        i += 1

    db.session.commit()
    session["client_id"] = new_client.id
    return redirect("/dashboard")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
```

### `routes/pages.py`
**Description:** Contains the routes responsible for rendering HTML templates for the dashboard, analysis page, settings, and profile.

```python
"""
Page routes: dashboard, analysis, settings, profile.
Single Responsibility: Only renders HTML pages (no business logic).
"""

from flask import Blueprint, render_template

from helpers import require_login

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/dashboard")
@require_login
def dashboard(client):
    return render_template("dashboard.html", client=client, page="dashboard")


@pages_bp.route("/analysis")
@require_login
def analysis(client):
    return render_template("analysis.html", client=client, page="analysis")


@pages_bp.route("/settings")
@require_login
def settings(client):
    return render_template("settings.html", client=client, page="settings")


@pages_bp.route("/profile")
@require_login
def profile(client):
    return render_template("profile.html", client=client, page="profile")

@pages_bp.route("/machine/<int:machine_id>")
@require_login
def machine(client, machine_id):
    # Retrieve machine just to ensure ownership. Real data fetched via JS.
    from models import Machine
    machine_record = Machine.query.get_or_404(machine_id)
    return render_template("machine.html", client=client, machine_id=machine_id, page="machine")
```

---

# JavaScript Files (Frontend Logic)

### `static/js/analysis.js`
**Description:** Handles chart rendering (using Chart.js) to show TRS trends and history comparisons across machines based on the selected period and metric.

```javascript
/**
 * analysis.js — TRS trend charts, metric toggles, comparison.
 */

let mainChart = null;
let compareChart = null;
let historyData = null;
let allMachinesData = null;
let activeMetrics = ['trs'];

const metricColors = { trs: '#3fb950', tdo: '#58a6ff', tp: '#a371f7', tq: '#d29922' };
const metricLabels = { trs: 'TRS', tdo: 'TDO (Disponibilité)', tp: 'TP (Performance)', tq: 'TQ (Qualité)' };

async function initAnalysis() {
    const res = await fetch('/api/usines');
    const usines = await res.json();
    const select = document.getElementById('machine-select');
    select.innerHTML = '';
    usines.forEach(u => {
        u.machines.forEach(m => {
            const opt = document.createElement('option');
            opt.value = m.id;
            opt.textContent = `${m.nom} (${u.nom})`;
            select.appendChild(opt);
        });
    });
    if (select.options.length > 0) {
        loadHistory();
        loadComparison();
    }
}

async function loadHistory() {
    const machineId = document.getElementById('machine-select').value;
    const days = document.getElementById('period-select').value;
    if (!machineId) return;
    const res = await fetch(`/api/machines/${machineId}/history?days=${days}`);
    historyData = await res.json();
    renderChart();
    renderStats();
    loadComparison();
}

function toggleMetric(btn) {
    const metric = btn.dataset.metric;
    if (activeMetrics.includes(metric)) {
        if (activeMetrics.length > 1) {
            activeMetrics = activeMetrics.filter(m => m !== metric);
            btn.classList.remove('active');
        }
    } else {
        activeMetrics.push(metric);
        btn.classList.add('active');
    }
    renderChart();
    renderStats();
}

function renderChart() {
    if (!historyData || !historyData.data.length) return;

    const labels = historyData.data.map(d => {
        const date = new Date(d.date);
        return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' });
    });

    const datasets = activeMetrics.map(metric => ({
        label: metricLabels[metric],
        data: historyData.data.map(d => d[metric]),
        borderColor: metricColors[metric],
        backgroundColor: metricColors[metric] + '15',
        fill: activeMetrics.length === 1,
        tension: 0.4, pointRadius: 3, pointHoverRadius: 6, borderWidth: 2,
    }));

    const ctx = document.getElementById('main-chart');
    if (mainChart) mainChart.destroy();

    document.getElementById('chart-title').textContent = `Évolution — ${historyData.machine_nom}`;
    document.getElementById('chart-subtitle').textContent =
        `${activeMetrics.map(m => metricLabels[m]).join(' · ')} sur ${historyData.data.length} jours`;

    mainChart = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: {
                legend: {
                    display: activeMetrics.length > 1,
                    labels: { color: '#8b949e', font: { size: 11 }, usePointStyle: true }
                },
                tooltip: {
                    backgroundColor: '#161b22', borderColor: '#30363d', borderWidth: 1,
                    titleColor: '#e6edf3', bodyColor: '#8b949e', padding: 12, displayColors: true,
                    callbacks: { label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y}%` }
                }
            },
            scales: {
                x: { grid: { color: '#21262d', drawBorder: false }, ticks: { color: '#484f58', font: { size: 10 } } },
                y: { min: 0, max: 100, grid: { color: '#21262d', drawBorder: false }, ticks: { color: '#484f58', font: { size: 10 }, callback: v => v + '%' } }
            }
        }
    });
}

function renderStats() {
    if (!historyData || !historyData.data.length) return;
    const metric = activeMetrics[0];
    const values = historyData.data.map(d => d[metric]);
    const avg = (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1);
    const max = Math.max(...values).toFixed(1);
    const min = Math.min(...values).toFixed(1);
    const trend = values.length >= 2 ? (values[values.length - 1] - values[0]).toFixed(1) : 0;

    const avgEl = document.getElementById('stat-avg');
    avgEl.textContent = avg + '%';
    avgEl.className = 'stat-value ' + (avg >= 85 ? 'c-green' : avg >= 70 ? 'c-yellow' : 'c-red');
    document.getElementById('stat-max').textContent = max + '%';
    document.getElementById('stat-min').textContent = min + '%';
    const trendEl = document.getElementById('stat-trend');
    trendEl.textContent = (trend >= 0 ? '+' : '') + trend + '%';
    trendEl.className = 'stat-value ' + (trend >= 0 ? 'c-green' : 'c-red');
}

async function loadComparison() {
    const days = document.getElementById('period-select').value;
    const res = await fetch(`/api/all-machines-history?days=${days}`);
    allMachinesData = await res.json();
    renderComparison();
}

function renderComparison() {
    if (!allMachinesData || !allMachinesData.length) return;
    const colors = ['#3fb950', '#58a6ff', '#a371f7', '#d29922', '#f85149', '#f778ba', '#79c0ff', '#56d364'];
    const allDates = new Set();
    allMachinesData.forEach(m => m.data.forEach(d => allDates.add(d.date)));
    const sortedDates = [...allDates].sort();
    const labels = sortedDates.map(d => {
        const date = new Date(d);
        return date.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' });
    });
    const datasets = allMachinesData.map((m, i) => {
        const dateMap = {};
        m.data.forEach(d => { dateMap[d.date] = d.trs; });
        return {
            label: `${m.machine_nom} (${m.usine_nom})`,
            data: sortedDates.map(d => dateMap[d] || null),
            borderColor: colors[i % colors.length],
            backgroundColor: 'transparent', tension: 0.4, pointRadius: 2, borderWidth: 2,
        };
    });
    const ctx = document.getElementById('compare-chart');
    if (compareChart) compareChart.destroy();
    compareChart = new Chart(ctx, {
        type: 'line', data: { labels, datasets },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            plugins: {
                legend: { labels: { color: '#8b949e', font: { size: 11 }, usePointStyle: true } },
                tooltip: { backgroundColor: '#161b22', borderColor: '#30363d', borderWidth: 1, titleColor: '#e6edf3', bodyColor: '#8b949e', padding: 12 }
            },
            scales: {
                x: { grid: { color: '#21262d', drawBorder: false }, ticks: { color: '#484f58', font: { size: 10 } } },
                y: { min: 0, max: 100, grid: { color: '#21262d', drawBorder: false }, ticks: { color: '#484f58', font: { size: 10 }, callback: v => v + '%' } }
            }
        }
    });
}

// Boot
initAnalysis();
```

### `static/js/base.js`
**Description:** Contains shared global UI logic such as toggling the sidebar, handling mobile sidebar states, showing toast notifications, and basic gauge generation logic.

```javascript
/**
 * base.js — Shared UI logic (sidebar, toast, gauge helper).
 * Loaded on every page via base.html.
 */

// ── Sidebar ──

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('collapsed');
    localStorage.setItem('sidebarCollapsed',
        document.getElementById('sidebar').classList.contains('collapsed'));
}

function toggleMobileSidebar() {
    document.getElementById('sidebar').classList.toggle('mobile-open');
}

// Restore sidebar state on load
if (localStorage.getItem('sidebarCollapsed') === 'true') {
    document.getElementById('sidebar').classList.add('collapsed');
}

// Close mobile sidebar on outside click
document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth <= 768 && sidebar.classList.contains('mobile-open')
        && !sidebar.contains(e.target) && !e.target.classList.contains('mobile-toggle')) {
        sidebar.classList.remove('mobile-open');
    }
});


// ── Toast Notifications ──

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    toast.innerHTML = `<span>${icon}</span> ${message}`;
    toast.className = 'toast show';
    setTimeout(() => { toast.className = 'toast'; }, 3000);
}


// ── Gauge Chart Helper ──

function createGauge(canvasId, value, label) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    let color;
    if (value >= 85) color = '#3fb950';
    else if (value >= 70) color = '#d29922';
    else color = '#f85149';

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: [color, '#21262d'],
                borderWidth: 0,
                circumference: 180,
                rotation: 270,
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
        }
    });
}
```

### `static/js/dashboard.js`
**Description:** Manages the main dashboard interface, fetching global stats from the API, rendering aggregate KPI blocks, setting up factory filters, and iterating gauge charts for all active machines.

```javascript
/**
 * dashboard.js — KPI rendering, gauge charts, usine filter.
 */

let dashboardData = null;
let activeFilter = 'all';

async function loadDashboard() {
    try {
        const res = await fetch('/api/dashboard-data');
        dashboardData = await res.json();
        renderKPIs();
        renderFilters();
        renderGauges();
    } catch (e) {
        console.error('Dashboard load error:', e);
    }
}

function renderKPIs() {
    const k = dashboardData.kpis;
    const trsEl = document.getElementById('kpi-trs');
    trsEl.textContent = k.trs_moyen + '%';
    trsEl.className = 'kpi-value ' + (k.trs_moyen >= 85 ? 'c-green' : k.trs_moyen >= 70 ? 'c-yellow' : 'c-red');

    document.getElementById('kpi-usines').textContent = k.usines_count;
    document.getElementById('kpi-machines').textContent = k.machines_count;

    const alertEl = document.getElementById('kpi-alerts');
    alertEl.textContent = k.alerts;
    if (k.alerts === 0) {
        alertEl.className = 'kpi-value c-green';
        alertEl.textContent = '0 ✓';
    }
}

function renderFilters() {
    const container = document.getElementById('usine-filter');
    let html = `<button class="usine-chip active" onclick="filterUsine('all')">Toutes</button>`;
    dashboardData.usines.forEach(u => {
        html += `<button class="usine-chip" onclick="filterUsine(${u.id})">${u.nom}</button>`;
    });
    container.innerHTML = html;
}

function filterUsine(id) {
    activeFilter = id;
    document.querySelectorAll('.usine-chip').forEach(c => c.classList.remove('active'));
    event.target.classList.add('active');
    renderGauges();
}

function renderGauges() {
    const grid = document.getElementById('gauges-grid');
    let machines = [];

    dashboardData.usines.forEach(u => {
        u.machines.forEach(m => {
            if (activeFilter === 'all' || activeFilter === u.id) {
                machines.push({...m, usine_nom: u.nom});
            }
        });
    });

    if (machines.length === 0) {
        grid.innerHTML = `
            <div class="empty-state" style="grid-column: 1/-1;">
                <div class="empty-icon">🏭</div>
                <h3>Aucune machine</h3>
                <p>Ajoutez des usines et machines dans les paramètres</p>
                <a href="/settings" class="btn btn-primary">⚙️ Configurer</a>
            </div>`;
        return;
    }

    grid.innerHTML = machines.map((m, idx) => {
        const trsClass = m.trs >= 85 ? 'badge-green' : m.trs >= 70 ? 'badge-yellow' : 'badge-red';
        return `
        <a href="/machine/${m.id}" class="machine-gauge-card" style="display:block; text-decoration:none; color:inherit;">
            <div class="machine-gauge-header">
                <div>
                    <div class="machine-gauge-name">${m.nom}</div>
                    <div class="machine-gauge-usine">📍 ${m.usine_nom}</div>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span class="badge ${trsClass}">${m.trs >= 85 ? 'Optimal' : m.trs >= 70 ? 'Attention' : 'Critique'}</span>
                    <span class="status-dot ${m.status}"></span>
                </div>
            </div>
            <div class="main-gauge">
                <canvas id="g-trs-${idx}" width="160" height="90"></canvas>
                <div class="main-gauge-value" style="color:${getColor(m.trs)}">${m.trs}%</div>
                <div class="main-gauge-label">TRS</div>
            </div>
            <div class="sub-gauges-row">
                <div class="mini-gauge">
                    <canvas id="g-tdo-${idx}" width="70" height="42"></canvas>
                    <div class="mini-gauge-value" style="color:${getColor(m.tdo)}">${m.tdo}%</div>
                    <div class="mini-gauge-label">TDO</div>
                </div>
                <div class="mini-gauge">
                    <canvas id="g-tp-${idx}" width="70" height="42"></canvas>
                    <div class="mini-gauge-value" style="color:${getColor(m.tp)}">${m.tp}%</div>
                    <div class="mini-gauge-label">TP</div>
                </div>
                <div class="mini-gauge">
                    <canvas id="g-tq-${idx}" width="70" height="42"></canvas>
                    <div class="mini-gauge-value" style="color:${getColor(m.tq)}">${m.tq}%</div>
                    <div class="mini-gauge-label">TQ</div>
                </div>
            </div>
        </a>`;
    }).join('');

    // Render gauges after DOM update
    setTimeout(() => {
        machines.forEach((m, idx) => {
            createBigGauge(`g-trs-${idx}`, m.trs);
            createMiniGauge(`g-tdo-${idx}`, m.tdo);
            createMiniGauge(`g-tp-${idx}`, m.tp);
            createMiniGauge(`g-tq-${idx}`, m.tq);
        });
    }, 50);
}

function getColor(val) {
    if (val >= 85) return '#3fb950';
    if (val >= 70) return '#d29922';
    return '#f85149';
}

function createBigGauge(id, value) {
    const ctx = document.getElementById(id);
    if (!ctx) return;
    const color = getColor(value);
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: [color, '#21262d'],
                borderWidth: 0, circumference: 180, rotation: 270,
            }]
        },
        options: {
            responsive: false, maintainAspectRatio: false, cutout: '70%',
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
        }
    });
}

function createMiniGauge(id, value) {
    const ctx = document.getElementById(id);
    if (!ctx) return;
    const color = getColor(value);
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: [color, '#21262d'],
                borderWidth: 0, circumference: 180, rotation: 270,
            }]
        },
        options: {
            responsive: false, maintainAspectRatio: false, cutout: '72%',
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
        }
    });
}

// Boot
loadDashboard();

// Refresh data every 30 seconds
setInterval(loadDashboard, 30000);
```

### `static/js/machine.js`
**Description:** Handles fetching data via the API for an individual machine in detail view and refreshing gauge cards / numeric KPIs dynamically.

```javascript
/**
 * machine.js — Detailed machine view logic, fetches machine data and node-red mock data
 */

let charts = {};

async function loadMachineDetails() {
    try {
        const res = await fetch(`/api/machines/${MACHINE_ID}/details`);
        if (!res.ok) {
            console.error('Error fetching machine details');
            return;
        }
        const data = await res.json();
        
        // Hide loader, show content
        document.getElementById('machine-loader').style.display = 'none';
        document.getElementById('machine-content').style.display = 'block';

        populateUI(data);
        renderGauges(data);
    } catch (e) {
        console.error('Failed to load machine details:', e);
    }
}

function getColor(val) {
    if (val >= 85) return '#3fb950'; // Green
    if (val >= 70) return '#d29922'; // Yellow
    return '#f85149'; // Red
}

function populateUI(m) {
    // Header
    document.getElementById('m-nom').textContent = m.nom;
    document.getElementById('m-usine').textContent = m.usine_nom;

    // Status Badge
    const statusBadge = document.getElementById('m-status-badge');
    const statusDot = document.getElementById('m-status-dot');
    document.getElementById('m-status-text').textContent = m.status.toUpperCase();
    
    statusBadge.className = 'badge ' + (m.status === 'online' ? 'badge-green' : 'badge-red');
    statusDot.className = 'status-dot ' + (m.status === 'online' ? 'online' : 'offline');

    // Production Data (Mock from Node-RED)
    const mock = m.mock_live_data;
    document.getElementById('m-pieces-ok').textContent = mock.pieces_ok;
    document.getElementById('m-pieces-rebus').textContent = mock.pieces_rebus;
    document.getElementById('m-cycle-time').innerHTML = `${mock.cycle_time} <span style="font-size: 13px; color: var(--text-secondary);">s/pièce</span>`;
    document.getElementById('m-cadence').innerHTML = `${m.cadence_theorique} <span style="font-size: 13px; color: var(--text-secondary);">pcs/min</span>`;
    
    // IoT environment
    document.getElementById('m-temp').innerHTML = `${mock.temperature} <span style="font-size: 13px; color: var(--text-secondary);">°C</span>`;
    document.getElementById('m-vib').innerHTML = `${mock.vibration} <span style="font-size: 13px; color: var(--text-secondary);">mm/s</span>`;

    // Sensors Type
    document.getElementById('s-type-vit').textContent = m.capteur_vitesse || 'Inconnu';
    document.getElementById('s-type-pcs').textContent = m.capteur_pieces || 'Inconnu';
    document.getElementById('s-type-disp').textContent = m.capteur_dispo || 'Inconnu';
    document.getElementById('s-type-qual').textContent = m.capteur_qualite || 'Inconnu';

    const sensorBadge = document.getElementById('m-sensor-health');
    sensorBadge.textContent = mock.sensor_health;
    sensorBadge.className = 'badge ' + (mock.sensor_health === 'Optimal' ? 'badge-green' : 'badge-red');
}

function renderGauges(m) {
    updateOrCreateGauge('gauge-trs', m.trs, 'm-trs-val', 'm-trs-badge');
    updateOrCreateGauge('gauge-tdo', m.tdo, 'm-tdo-val', null);
    updateOrCreateGauge('gauge-tp', m.tp, 'm-tp-val', null);
    updateOrCreateGauge('gauge-tq', m.tq, 'm-tq-val', null);
}

function updateOrCreateGauge(canvasId, value, valueId, badgeId) {
    document.getElementById(valueId).textContent = value + '%';
    document.getElementById(valueId).style.color = getColor(value);
    
    if (badgeId) {
        const badge = document.getElementById(badgeId);
        badge.textContent = value >= 85 ? 'Optimal' : value >= 70 ? 'Attention' : 'Critique';
        badge.className = 'badge ' + (value >= 85 ? 'badge-green' : value >= 70 ? 'badge-yellow' : 'badge-red');
    }

    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    const color = getColor(value);

    if (charts[canvasId]) {
        // Update existing chart smoothly
        charts[canvasId].data.datasets[0].data = [value, 100 - value];
        charts[canvasId].data.datasets[0].backgroundColor[0] = color;
        charts[canvasId].update();
    } else {
        // Create new chart
        charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [value, 100 - value],
                    backgroundColor: [color, '#21262d'],
                    borderWidth: 0, circumference: 180, rotation: 270,
                }]
            },
            options: {
                responsive: true, maintainAspectRatio: false, cutout: '75%',
                plugins: { legend: { display: false }, tooltip: { enabled: false } },
            }
        });
    }
}

// Initial pull
loadMachineDetails();

// Refresh every 30 seconds
setInterval(loadMachineDetails, 30000);
```

### `static/js/profile.js`
**Description:** Logic for the user profile form, submitting PUT requests to update personal information and change passwords.

```javascript
/**
 * profile.js — Personal info update and password change.
 */

async function saveProfile() {
    const data = {
        prenom: document.getElementById('edit-prenom').value,
        nom: document.getElementById('edit-nom').value,
        telephone: document.getElementById('edit-telephone').value,
        entreprise: document.getElementById('edit-entreprise').value,
        secteur: document.getElementById('edit-secteur').value,
    };

    const res = await fetch('/api/profile', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    if (res.ok) {
        showToast('Profil mis à jour');
        document.getElementById('display-name').textContent = data.prenom + ' ' + data.nom;
        document.getElementById('display-entreprise').textContent = data.entreprise || '—';
        document.getElementById('display-secteur').textContent = data.secteur || '—';
        document.getElementById('avatar-initials').textContent =
            (data.prenom[0] || '') + (data.nom[0] || '');

        const indicator = document.getElementById('info-saved');
        indicator.classList.add('show');
        setTimeout(() => indicator.classList.remove('show'), 3000);
    } else {
        showToast('Erreur lors de la mise à jour', 'error');
    }
}

async function changePassword() {
    const currentPwd = document.getElementById('current-password').value;
    const newPwd = document.getElementById('new-password').value;
    const confirmPwd = document.getElementById('confirm-password').value;

    if (!currentPwd || !newPwd) {
        showToast('Veuillez remplir tous les champs', 'error');
        return;
    }
    if (newPwd.length < 8) {
        showToast('Le nouveau mot de passe doit avoir au moins 8 caractères', 'error');
        return;
    }
    if (newPwd !== confirmPwd) {
        showToast('Les mots de passe ne correspondent pas', 'error');
        return;
    }

    const res = await fetch('/api/profile', {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ current_password: currentPwd, new_password: newPwd })
    });

    if (res.ok) {
        showToast('Mot de passe mis à jour');
        document.getElementById('current-password').value = '';
        document.getElementById('new-password').value = '';
        document.getElementById('confirm-password').value = '';
        const indicator = document.getElementById('pwd-saved');
        indicator.classList.add('show');
        setTimeout(() => indicator.classList.remove('show'), 3000);
    } else {
        const err = await res.json();
        showToast(err.error || 'Erreur', 'error');
    }
}
```

### `static/js/settings.js`
**Description:** Handles the Settings interface, fetching and rendering the list of factories and machines, and handling modal interactions/form submissions to add, edit, and delete elements in the database.

```javascript
/**
 * settings.js — CRUD for usines and machines.
 */

async function loadSettings() {
    const res = await fetch('/api/usines');
    const usines = await res.json();
    renderUsines(usines);
}

function renderUsines(usines) {
    const container = document.getElementById('usines-list');
    if (usines.length === 0) {
        container.innerHTML = `
            <div class="card" style="text-align:center;padding:48px;">
                <div style="font-size:48px;margin-bottom:16px;opacity:0.5;">🏭</div>
                <h3 style="font-size:16px;margin-bottom:8px;">Aucune usine configurée</h3>
                <p style="font-size:13px;color:var(--text-secondary);margin-bottom:16px;">
                    Commencez par ajouter votre première usine
                </p>
                <button class="btn btn-primary" onclick="openUsineModal()">+ Ajouter une usine</button>
            </div>`;
        return;
    }

    container.innerHTML = usines.map(u => `
        <div class="usine-block">
            <div class="usine-block-header" onclick="this.parentElement.querySelector('.usine-block-body').style.display = this.parentElement.querySelector('.usine-block-body').style.display === 'none' ? 'block' : 'none'">
                <div class="usine-block-title">
                    <span style="font-size:20px;">🏭</span>
                    <div>
                        <div class="usine-block-name">${u.nom}</div>
                        <div class="usine-block-info">📍 ${u.ville || '—'}, ${u.pays || '—'} · ${u.machines_count} machines · ${u.postes} poste(s)</div>
                    </div>
                </div>
                <div class="usine-block-actions" onclick="event.stopPropagation()">
                    <button class="btn btn-secondary btn-sm" onclick="openUsineModal(${u.id}, '${escHtml(u.nom)}', '${escHtml(u.ville||'')}', '${escHtml(u.pays||'Tunisie')}', ${u.postes}, ${u.tr})">✏️ Modifier</button>
                    <button class="btn btn-danger btn-sm" onclick="confirmDelete('usine', ${u.id}, '${escHtml(u.nom)}')">🗑️</button>
                </div>
            </div>
            <div class="usine-block-body">
                ${u.machines.length > 0 ? `
                <div class="machines-table-wrap">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Machine</th><th>Cadence</th><th>TRS</th>
                                <th>Status</th><th>Capteurs</th><th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${u.machines.map(m => `
                            <tr>
                                <td style="font-weight:500;">${m.nom}</td>
                                <td>${m.cadence_theorique} pcs/min</td>
                                <td>
                                    <span class="${m.trs >= 85 ? 'c-green' : m.trs >= 70 ? 'c-yellow' : 'c-red'}" style="font-family:'Space Mono',monospace;font-weight:700;">
                                        ${m.trs}%
                                    </span>
                                </td>
                                <td><span class="status-dot ${m.status}"></span> ${m.status}</td>
                                <td style="font-size:11px;color:var(--text-secondary);">
                                    ${m.capteur_vitesse} · ${m.capteur_pieces}
                                </td>
                                <td>
                                    <div class="actions">
                                        <button class="btn btn-secondary btn-sm btn-icon" onclick="openMachineModal(${u.id}, ${m.id}, '${escHtml(m.nom)}', ${m.cadence_theorique}, ${m.seuil_vibration}, ${m.seuil_piece_cm}, ${m.delai_mesures}, '${m.capteur_vitesse}', '${m.capteur_pieces}', '${m.capteur_dispo}', '${m.capteur_qualite}')">✏️</button>
                                        <button class="btn btn-danger btn-sm btn-icon" onclick="confirmDelete('machine', ${m.id}, '${escHtml(m.nom)}')">🗑️</button>
                                    </div>
                                </td>
                            </tr>`).join('')}
                        </tbody>
                    </table>
                </div>` : `
                <div class="empty-machines"><p>Aucune machine dans cette usine</p></div>`}
                <div class="add-machine-row">
                    <button class="btn btn-secondary btn-sm" onclick="openMachineModal(${u.id})">+ Ajouter une machine</button>
                </div>
            </div>
        </div>
    `).join('');
}

function escHtml(str) {
    return String(str).replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

// ── Usine Modal ──

function openUsineModal(id, nom, ville, pays, postes, tr) {
    document.getElementById('usine-edit-id').value = id || '';
    document.getElementById('usine-nom').value = nom || '';
    document.getElementById('usine-ville').value = ville || '';
    document.getElementById('usine-pays').value = pays || 'Tunisie';
    document.getElementById('usine-postes').value = postes || 1;
    document.getElementById('usine-tr').value = tr || 8;
    document.getElementById('usine-modal-title').textContent = id ? "Modifier l'usine" : 'Ajouter une usine';
    document.getElementById('usine-modal').classList.add('active');
}
function closeUsineModal() { document.getElementById('usine-modal').classList.remove('active'); }

async function saveUsine() {
    const id = document.getElementById('usine-edit-id').value;
    const data = {
        nom: document.getElementById('usine-nom').value,
        ville: document.getElementById('usine-ville').value,
        pays: document.getElementById('usine-pays').value,
        postes: parseInt(document.getElementById('usine-postes').value),
        tr: parseInt(document.getElementById('usine-tr').value),
    };
    if (!data.nom) { showToast('Le nom est obligatoire', 'error'); return; }
    const url = id ? `/api/usines/${id}` : '/api/usines';
    const method = id ? 'PUT' : 'POST';
    await fetch(url, { method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    closeUsineModal();
    showToast(id ? 'Usine modifiée' : 'Usine ajoutée');
    loadSettings();
}

// ── Machine Modal ──

function openMachineModal(usineId, machineId, nom, cadence, seuilV, seuilP, delai, cv, cp, cd, cq) {
    document.getElementById('machine-usine-id').value = usineId || '';
    document.getElementById('machine-edit-id').value = machineId || '';
    document.getElementById('machine-nom').value = nom || '';
    document.getElementById('machine-cadence').value = cadence || '';
    document.getElementById('machine-seuil-vibration').value = seuilV || '';
    document.getElementById('machine-seuil-piece-cm').value = seuilP || '';
    document.getElementById('machine-delai').value = delai || '';
    document.getElementById('machine-capteur-vitesse').value = cv || 'simulation';
    document.getElementById('machine-capteur-pieces').value = cp || 'simulation';
    document.getElementById('machine-capteur-dispo').value = cd || 'simulation';
    document.getElementById('machine-capteur-qualite').value = cq || 'simulation';
    document.getElementById('machine-modal-title').textContent = machineId ? 'Modifier la machine' : 'Ajouter une machine';
    document.getElementById('machine-modal').classList.add('active');
}
function closeMachineModal() { document.getElementById('machine-modal').classList.remove('active'); }

async function saveMachine() {
    const machineId = document.getElementById('machine-edit-id').value;
    const usineId = document.getElementById('machine-usine-id').value;
    const data = {
        nom: document.getElementById('machine-nom').value,
        cadence_theorique: parseFloat(document.getElementById('machine-cadence').value) || 50,
        seuil_vibration: parseFloat(document.getElementById('machine-seuil-vibration').value) || 0.0,
        seuil_piece_cm: parseFloat(document.getElementById('machine-seuil-piece-cm').value) || 0.0,
        delai_mesures: parseInt(document.getElementById('machine-delai').value) || 60,
        capteur_vitesse: document.getElementById('machine-capteur-vitesse').value,
        capteur_pieces: document.getElementById('machine-capteur-pieces').value,
        capteur_dispo: document.getElementById('machine-capteur-dispo').value,
        capteur_qualite: document.getElementById('machine-capteur-qualite').value,
    };
    if (!data.nom) { showToast('Le nom est obligatoire', 'error'); return; }
    let url, method;
    if (machineId) { url = `/api/machines/${machineId}`; method = 'PUT'; }
    else { url = `/api/usines/${usineId}/machines`; method = 'POST'; }
    await fetch(url, { method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
    closeMachineModal();
    showToast(machineId ? 'Machine modifiée' : 'Machine ajoutée');
    loadSettings();
}

// ── Confirm Delete ──

let deleteTarget = {};
function confirmDelete(type, id, name) {
    deleteTarget = { type, id };
    document.getElementById('confirm-message').textContent =
        `Êtes-vous sûr de vouloir supprimer "${name}" ? Cette action est irréversible.`;
    document.getElementById('confirm-btn').onclick = executeDelete;
    document.getElementById('confirm-modal').classList.add('active');
}
function closeConfirm() { document.getElementById('confirm-modal').classList.remove('active'); }

async function executeDelete() {
    const url = deleteTarget.type === 'usine'
        ? `/api/usines/${deleteTarget.id}`
        : `/api/machines/${deleteTarget.id}`;
    await fetch(url, { method: 'DELETE' });
    closeConfirm();
    showToast('Supprimé avec succès');
    loadSettings();
}

// Boot
loadSettings();
```

---

# Configuration & Variables

### `.env` & `.env.example`
**Description:** Environment variable files to store sensitive configuration like `SECRET_KEY`, `DATABASE_URL` (for Postgres connection string), and `API_KEY` (for Node-RED authentication).

---

# HTML Templates (Descriptions Only)

- `templates/analysis.html`: Layout for the historical analysis page, containing the canvas elements for Chart.js trend lines and metric toggles.
- `templates/base.html`: The base HTML template containing the common layout (sidebar navigation, header structure, metadata) inherited by all other templates.
- `templates/dashboard.html`: The main dashboard view presenting all machines as gauge cards and summarizing high-level global KPIs.
- `templates/login.html`: The authentication page UI containing both login and user registration forms along with factory initialization inputs.
- `templates/machine.html`: The individual detailed view for a single machine, rendering its specific gauge charts, real-time sensor variables, and configuration.
- `templates/profile.html`: Form layout permitting authenticated users to update their personal information and securely change their passwords.
- `templates/settings.html`: The management UI containing dynamic tables and lists for adding, modifying, and deleting factories and machine records.
- `templates/usine.html`: Rendered view containing factory-specific data or list structure.

---

# CSS Files (Descriptions Only)

- `static/css/analysis.css`: Styling specific to the analysis page components such as metric toggle buttons and chart containers.
- `static/css/base.css`: Global application styles defining CSS root variables (color palette, spacing), typography, sidebar layouts, and common components like standard buttons, toast notifications, and inputs.
- `static/css/dashboard.css`: Styling for the main dashboard grid structure, machine gauge cards, and KPI banner layouts.
- `static/css/machine.css`: Styling tailored for the detailed machine statistics view and live data block configurations.
- `static/css/profile.css`: Layout constraints and visual styling for the user profile form grid.
- `static/css/settings.css`: Styling for the CRUD operations page (lists, accordion behaviors on factory items, data tables, and modal overlay popups).
