import uuid
from sqlalchemy import Column, String, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from shared.database import Base
from sqlalchemy.orm import relationship



class Client(Base):
    """User account — represents a factory owner."""
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    firstname = Column(String)
    lastname = Column(String)
    entreprise = Column(String)
    phone_number = Column(String)
    sector = Column(String)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    factories = relationship(
        "Factory", backref="client", lazy=True, cascade="all, delete-orphan"
    )
