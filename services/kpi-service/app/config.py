import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "").strip()
    API_KEY = os.environ.get("API_KEY", "").strip()
