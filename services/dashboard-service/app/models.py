import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db import db


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    entreprise = db.Column(db.String)
    phone_number = db.Column(db.String)
    sector = db.Column(db.String)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    factories = db.relationship("Factory", backref="client", lazy=True, cascade="all, delete-orphan")


class Factory(db.Model):
    __tablename__ = "factories"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = db.Column(UUID(as_uuid=True), db.ForeignKey("clients.id", ondelete="CASCADE"))
    name = db.Column(db.String, nullable=False)
    town = db.Column(db.String)
    country = db.Column(db.String)
    required_time = db.Column(db.Integer, default=8)
    positions = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    machines = db.relationship("Machine", backref="factory", lazy=True, cascade="all, delete-orphan")


class Machine(db.Model):
    __tablename__ = "machines"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    factory_id = db.Column(UUID(as_uuid=True), db.ForeignKey("factories.id", ondelete="CASCADE"))
    name = db.Column(db.String, nullable=False)
    theoretical_speed = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, default="offline")

    trs = db.Column(db.Float, default=0.0)
    tdo = db.Column(db.Float, default=0.0)
    tp = db.Column(db.Float, default=0.0)
    tq = db.Column(db.Float, default=0.0)

    vibration_threshold = db.Column(db.Float, default=0.0)
    piece_cm_threshold = db.Column(db.Float, default=0.0)
    measurement_delays = db.Column(db.Integer, default=60)
    
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)

    history = db.relationship("KpiSnapshot", backref="machine", lazy=True, cascade="all, delete-orphan")


class KpiSnapshot(db.Model):
    __tablename__ = "kpi_snapshots"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = db.Column(UUID(as_uuid=True), db.ForeignKey("clients.id"))
    factory_id = db.Column(UUID(as_uuid=True), db.ForeignKey("factories.id"))
    machine_id = db.Column(UUID(as_uuid=True), db.ForeignKey("machines.id"))

    trs = db.Column(db.Float, default=0.0)
    tdo = db.Column(db.Float, default=0.0)
    tp = db.Column(db.Float, default=0.0)
    tq = db.Column(db.Float, default=0.0)

    total_pieces = db.Column(db.Integer, default=0)
    good_pieces = db.Column(db.Integer, default=0)
    defective_pieces = db.Column(db.Integer, default=0)
    runtime_seconds = db.Column(db.Float, default=0)

    recorded_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)


class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = db.Column(UUID(as_uuid=True), db.ForeignKey("clients.id"))
    factory_id = db.Column(UUID(as_uuid=True), db.ForeignKey("factories.id"))
    machine_id = db.Column(UUID(as_uuid=True), db.ForeignKey("machines.id"))
    device_id = db.Column(db.String)
    event_type = db.Column(db.String, nullable=False)
    value = db.Column(db.String)
    event_metadata = db.Column(JSONB, default={})
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
