from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os

# The DATABASE_URL will be provided by Docker Compose or Cloud Environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the engine - this is the actual connection to the database
engine = create_engine(DATABASE_URL)

# sessionmaker creates a factory for new Session objects
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# scoped_session ensures that each request has its own session that is shared 
# across the thread, which is standard for web applications.
db_session = scoped_session(SessionLocal)
