import uuid
from sqlalchemy import Column, String, Float, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from shared.database import Base
from sqlalchemy.orm import relationship, backref

class Machine(Base):
    __tablename__ = "machines"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    factory_id = Column(UUID(as_uuid=True), ForeignKey("factories.id"))

    name = Column(String, nullable=False)

    theoretical_speed = Column(Float, nullable=False)

    status = Column(String, default="offline")

    vibration_threshold = Column(Float, default=0.0)
    piece_cm_threshold = Column(Float, default=0.0)
    measurement_delays = Column(Integer, default=60)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    device = relationship("Device", backref=backref("machine", uselist=False), uselist=False)
    history = relationship(
        "KpiSnapshot", backref="machine", lazy=True, cascade="all, delete-orphan"
    )
    