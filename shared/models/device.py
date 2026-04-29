import uuid
from sqlalchemy import Column, String, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from shared.database import Base
from sqlalchemy.orm import relationship


class Device(Base):
    __tablename__ = "devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(String, unique=True, nullable=False)

    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"))
    factory_id = Column(UUID(as_uuid=True), ForeignKey("factories.id", ondelete="CASCADE"))
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machines.id", ondelete="SET NULL"))

    status = Column(String, default="offline")
    last_seen = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Optional relationships
    client = relationship("Client", backref="devices")
    factory = relationship("Factory", backref="devices")
