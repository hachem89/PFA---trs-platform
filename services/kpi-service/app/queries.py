from datetime import datetime, timedelta
from sqlalchemy import desc
from shared.models.event import Event
from shared.models.machine import Machine

def get_window_events(db_session, machine_id, start_time, end_time):
    """Fetches all events for a machine within a specific time window."""
    return db_session.query(Event).filter(
        Event.machine_id == machine_id,
        Event.timestamp >= start_time,
        Event.timestamp < end_time
    ).order_by(Event.timestamp.asc()).all()

def get_last_state_before(db_session, machine_id, start_time):
    """
    Fetches the most recent 'machine_state' event before the window starts.
    Crucial for calculating runtime continuity.
    """
    last_event = db_session.query(Event).filter(
        Event.machine_id == machine_id,
        Event.event_type == 'machine_state',
        Event.timestamp < start_time
    ).order_by(desc(Event.timestamp)).first()
    
    if last_event:
        return last_event.value
    return 'stopped'  # Default if no history exists
