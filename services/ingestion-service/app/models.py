from app.db import db
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from datetime import datetime

class Machine(db.Model):
    __tablename__ = "machines"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    factory_id = db.Column(UUID(as_uuid=True), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    theoretical_speed = db.Column(db.Float, nullable=False)
    vibration_threshold = db.Column(db.Float, default=0.0)
    piece_cm_threshold = db.Column(db.Float, default=0.0)
    measurement_delays = db.Column(db.Integer, default=60)
    
    # Cached KPIs
    trs = db.Column(db.Float, default=0.0)
    tdo = db.Column(db.Float, default=0.0)
    tp = db.Column(db.Float, default=0.0)
    tq = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default="offline")

    events = db.relationship("Event", back_populates="machine", lazy=True, cascade="all, delete-orphan")

class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    machine_id = db.Column(UUID(as_uuid=True), db.ForeignKey("machines.id"), nullable=False)
    event_type = db.Column(db.String(50), nullable=False) # 'piece_detected', 'state_change', 'sensor_reading'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    event_metadata = db.Column(JSONB, default=dict)

    machine = db.relationship("Machine", back_populates="events")
