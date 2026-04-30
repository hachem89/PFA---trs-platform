import os
from dotenv import load_dotenv

# Load environment variables from the .env file located in the root of the project
# We calculate the path to the root .env file relative to this file
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Standard Flask configuration class."""
    
    # Secret key for signing session cookies
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # Database connection string
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Disable tracking to save resources
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Other potential settings (DEBUG, PORT, etc.)
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
