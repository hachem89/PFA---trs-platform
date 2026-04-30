from flask import Blueprint, render_template, request, redirect, session, url_for
from app.db import db_session
from shared.models.client import Client
from shared.models.factory import Factory
from shared.models.machine import Machine

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/")
def index():
    return redirect(url_for("auth.login"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        
        # Querying using our shared Client model
        client = db_session.query(Client).filter_by(email=email).first()
        
        if client and client.password == password:
            # We store the ID as a string in the session
            session["client_id"] = str(client.id)
            return redirect(url_for("dashboard"))
            
        return render_template("login.html", error="Email ou mot de passe incorrect")
    
    return render_template("login.html")

@auth_bp.route("/register", methods=["POST"])
def register():
    # Extracted fields using the NEW naming conventions from your updated templates
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()
    firstname = request.form.get("firstname", "")
    lastname = request.form.get("lastname", "")
    entreprise = request.form.get("entreprise", "")
    phone_number = request.form.get("phone_number", "")
    sector = request.form.get("sector", "")

    # Validation: Check if email already exists
    if db_session.query(Client).filter_by(email=email).first():
        return render_template("login.html", error="Cet email est déjà utilisé")

    # 1. Create the Client (User)
    new_client = Client(
        email=email, 
        password=password, 
        firstname=firstname, 
        lastname=lastname,
        entreprise=entreprise, 
        phone_number=phone_number, 
        sector=sector
    )
    db_session.add(new_client)
    db_session.flush() # Flush to get the new_client.id before committing

    # 2. Create the Factory (Usine)
    # Mapping old 'tr' -> 'required_time' and 'postes' -> 'positions'
    new_factory = Factory(
        client_id=new_client.id,
        name=request.form.get("factory_name", "Usine principale"),
        town=request.form.get("factory_city", ""),
        country=request.form.get("factory_country", "Tunisie"),
        required_time=int(request.form.get("factory_tr", 8)),
        positions=int(request.form.get("number_of_shifts", 1)),
    )
    db_session.add(new_factory)
    db_session.flush()

    # 3. Create Machines
    i = 0
    while request.form.get(f"machine_name_{i}"):
        new_machine = Machine(
            factory_id=new_factory.id,
            name=request.form.get(f"machine_name_{i}"),
            # Mapping 'cadence' -> 'theoretical_speed' and 'delai' -> 'measurement_delays'
            theoretical_speed=float(request.form.get(f"machine_cadence_{i}", 50)),
            status="offline",
            vibration_threshold=float(request.form.get(f"machine_vibration_threshold_{i}", 0.0)),
            piece_cm_threshold=float(request.form.get(f"machine_piece_cm_threshold_{i}", 0.0)),
            measurement_delays=int(request.form.get(f"machine_delay_{i}", 60)),
        )
        db_session.add(new_machine)
        # Note: seed_demo_history was intentionally omitted per your request
        i += 1

    # Commit all changes to the database
    db_session.commit()
    
    session["client_id"] = str(new_client.id)
    return redirect(url_for("dashboard"))

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
