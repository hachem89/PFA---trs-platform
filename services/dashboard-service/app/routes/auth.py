from flask import Blueprint, render_template, request, redirect, session
from app.db import db
from app.models import Client, Factory, Machine

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
            session["client_id"] = str(client.id)
            return redirect("/dashboard")
        return render_template("login.html", error="Incorrect email or password")
    return render_template("login.html")

@auth_bp.route("/register", methods=["POST"])
def register():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()
    firstname = request.form.get("prenom", "")
    lastname = request.form.get("nom", "")
    entreprise = request.form.get("entreprise", "")
    phone_number = request.form.get("telephone", "")
    sector = request.form.get("secteur", "")

    if Client.query.filter_by(email=email).first():
        return render_template("login.html", error="This email is already used")

    new_client = Client(
        email=email, password=password, firstname=firstname, lastname=lastname,
        entreprise=entreprise, phone_number=phone_number, sector=sector,
    )
    db.session.add(new_client)
    db.session.flush()

    new_factory = Factory(
        client_id=new_client.id,
        name=request.form.get("usine_nom", "Main Factory"),
        town=request.form.get("usine_ville", ""),
        country=request.form.get("usine_pays", "Tunisia"),
        required_time=int(request.form.get("usine_tr", 8)),
        positions=int(request.form.get("usine_postes", 1)),
    )
    db.session.add(new_factory)
    db.session.flush()

    i = 0
    while request.form.get(f"machine_nom_{i}"):
        new_machine = Machine(
            factory_id=new_factory.id,
            name=request.form.get(f"machine_nom_{i}"),
            theoretical_speed=float(request.form.get(f"machine_cadence_{i}", 50)),
            trs=0, tdo=0, tp=0, tq=0,
            status="offline",
            vibration_threshold=float(request.form.get(f"machine_seuil_vibration_{i}", 0.0)),
            piece_cm_threshold=float(request.form.get(f"machine_seuil_piece_cm_{i}", 0.0)),
            measurement_delays=int(request.form.get(f"machine_delai_{i}", 60)),
        )
        db.session.add(new_machine)
        db.session.flush()
        i += 1

    db.session.commit()
    session["client_id"] = str(new_client.id)
    return redirect("/dashboard")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
