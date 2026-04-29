from app.db import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime

class Factory(db.Model):
    __tablename__ = "factories"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    required_time = db.Column(db.Integer, default=8)

    machines = db.relationship("Machine", back_populates="factory", lazy=True)

class Machine(db.Model):
    __tablename__ = "machines"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    factory_id = db.Column(UUID(as_uuid=True), db.ForeignKey("factories.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    theoretical_speed = db.Column(db.Float, nullable=False)
    
    # Cached KPIs
    trs = db.Column(db.Float, default=0.0)
    tdo = db.Column(db.Float, default=0.0)
    tp = db.Column(db.Float, default=0.0)
    tq = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="offline")

    factory = db.relationship("Factory", back_populates="machines")

class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = db.Column(UUID(as_uuid=True), db.ForeignKey("machines.id"), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    event_metadata = db.Column(JSONB, default=dict)

class KpiSnapshot(db.Model):
    __tablename__ = "kpi_snapshots"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = db.Column(UUID(as_uuid=True), db.ForeignKey("machines.id"), nullable=False)
    trs = db.Column(db.Float, default=0.0)
    tdo = db.Column(db.Float, default=0.0)
    tp = db.Column(db.Float, default=0.0)
    tq = db.Column(db.Float, default=0.0)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
