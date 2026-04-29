from shared.models.event import Event
from app.db import SessionLocal

def create_event(data):
    db = SessionLocal()

    try:
        event = Event(
            client_id=data.get("client_id"),
            factory_id=data.get("factory_id"),
            machine_id=data.get("machine_id"),
            device_id=data.get("device_id"),
            event_type=data.get("event_type"),
            value=data.get("value"),
            event_metadata=data.get("event_metadata", {})
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return event

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()