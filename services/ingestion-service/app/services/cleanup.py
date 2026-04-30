from datetime import datetime, timedelta
from sqlalchemy import delete
from app.db import SessionLocal
from shared.models.event import Event

def cleanup_old_events(days=3):
    """
    Deletes events older than 'days'.
    We keep it small (3 days) for development to save database space.
    """
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # SQL Alchemy delete statement
        stmt = delete(Event).where(Event.timestamp < cutoff)
        
        result = db.execute(stmt)
        db.commit()
        
        if result.rowcount > 0:
            print(f"LOG [Cleanup]: Deleted {result.rowcount} old events (older than {days} days).")
            
    except Exception as e:
        print(f"ERROR [Cleanup]: {e}")
        db.rollback()
    finally:
        db.close()
