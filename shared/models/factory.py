import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from shared.database import Base


class Factory(Base):
    __tablename__ = "factories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"))

    name = Column(String, nullable=False)
    town = Column(String)
    country = Column(String)

    required_time = Column(Integer, default=8)
    positions = Column(Integer, default=1)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    machines = relationship(
        "Machine", backref="factory", lazy=True, cascade="all, delete-orphan"
    )
