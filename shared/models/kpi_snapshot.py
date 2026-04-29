import uuid
from sqlalchemy import Column, Float, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from shared.database import Base


class KpiSnapshot(Base):
    __tablename__ = "kpi_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    factory_id = Column(UUID(as_uuid=True), ForeignKey("factories.id"))
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"))

    trs = Column(Float, default=0.0)
    tdo = Column(Float, default=0.0)
    tp = Column(Float, default=0.0)
    tq = Column(Float, default=0.0)

    total_pieces = Column(Integer, default=0)
    good_pieces = Column(Integer, default=0)
    defective_pieces = Column(Integer, default=0)

    runtime_seconds = Column(Float, default=0)

    recorded_at = Column(TIMESTAMP(timezone=True), server_default=func.now())