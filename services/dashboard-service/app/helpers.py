from functools import wraps
from flask import session, redirect, url_for
from app.db import db_session
from shared.models.client import Client

def require_login(f):
    """Decorator to ensure user is logged in before accessing a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'client_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_client():
    """Helper to fetch the current logged-in client object from the DB."""
    if 'client_id' in session:
        # We use .get() which works with the primary key (UUID in our case)
        return db_session.query(Client).get(session['client_id'])
    return None
