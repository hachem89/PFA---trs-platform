import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from shared.database import Base


class Machine(Base):
    __tablename__ = "machines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    factory_id = Column(UUID(as_uuid=True), ForeignKey("factories.id", ondelete="CASCADE"))

    name = Column(String, nullable=False)

    theoretical_speed = Column(Float, nullable=False)

    status = Column(String, default="offline")

    # Current KPI values (updated by KPI service for dashboard fast-read)
    trs = Column(Float, default=0.0)
    tdo = Column(Float, default=0.0)
    tp = Column(Float, default=0.0)
    tq = Column(Float, default=0.0)

    # Sensor thresholds
    vibration_threshold = Column(Float, default=0.0)
    piece_cm_threshold = Column(Float, default=0.0)
    measurement_delays = Column(Integer, default=60)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    device = relationship("Device", backref="machine", uselist=False)
    history = relationship(
        "KpiSnapshot", backref="machine", lazy=True, cascade="all, delete-orphan"
    )