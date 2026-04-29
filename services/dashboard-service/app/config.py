import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback_secret_key").strip()
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "").strip()
    API_KEY = os.environ.get("API_KEY", "").strip()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
