import uuid
from sqlalchemy import Column, String, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from shared.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"))
    factory_id = Column(UUID(as_uuid=True), ForeignKey("factories.id"))
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id"))

    device_id = Column(String)

    event_type = Column(String, nullable=False)
    value = Column(String)

    event_metadata = Column(JSONB, default={})

    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
