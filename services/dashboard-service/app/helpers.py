from functools import wraps
from flask import redirect, session
from app.db import db
from app.models import Client

def get_current_client():
    """Return the logged-in Client or None."""
    if "client_id" not in session:
        return None
    return db.session.get(Client, session["client_id"])


def require_login(f):
    """Decorator — redirects to /login if not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        client = get_current_client()
        if not client:
            return redirect("/login")
        return f(client, *args, **kwargs)
    return decorated
