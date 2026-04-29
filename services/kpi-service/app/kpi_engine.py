from app.db import db
from app.models import Machine, Factory, Event, KpiSnapshot
from datetime import datetime, timedelta

def calculate_kpis():
    """
    Calculates KPIs (TRS, TDO, TP, TQ) for all machines based on recent events.
    Updates the Machine table and creates a KpiSnapshot.
    """
    now = datetime.utcnow()
    # Let's say we calculate based on the last hour of data
    one_hour_ago = now - timedelta(hours=1)

    machines = Machine.query.all()
    
    for machine in machines:
        factory = db.session.get(Factory, machine.factory_id)
        if not factory:
            continue
            
        # Get events for this machine in the last hour
        events = Event.query.filter(
            Event.machine_id == machine.id,
            Event.timestamp >= one_hour_ago
        ).all()

        # Basic counters
        total_pieces = 0
        good_pieces = 0
        bad_pieces = 0
        downtime_seconds = 0
        operating_time_seconds = 3600  # assuming 1 hour analysis window
        
        # In a real scenario, you'd calculate downtime by parsing state_change events.
        # For this prototype, we'll make a simplified calculation:
        for event in events:
            if event.event_type == "piece_detected":
                total_pieces += 1
                is_good = event.event_metadata.get("is_good", True)
                if is_good:
                    good_pieces += 1
                else:
                    bad_pieces += 1
            elif event.event_type == "state_change":
                state = event.event_metadata.get("state")
                # e.g., if we track downtime exactly, we'd calculate time diffs
                if state == "error" or state == "offline":
                    # Mock logic: assume each error event signifies 5 mins of downtime
                    downtime_seconds += 300

        # Prevent operating time from going negative
        if downtime_seconds > operating_time_seconds:
            downtime_seconds = operating_time_seconds

        # 1. TDO (Disponibilité / Availability)
        # Ratio of Operating Time / Planned Production Time
        planned_production_time = operating_time_seconds
        actual_operating_time = planned_production_time - downtime_seconds
        
        tdo = (actual_operating_time / planned_production_time) * 100 if planned_production_time > 0 else 0.0
        
        # 2. TP (Performance)
        # Ratio of Net Operating Time / Actual Operating Time
        # Net Operating Time = Ideal Cycle Time * Total Pieces
        # Ideal Cycle Time = 60 / Theoretical Speed (parts/min)
        if machine.theoretical_speed > 0:
            ideal_cycle_time = 60.0 / machine.theoretical_speed
            net_operating_time = ideal_cycle_time * total_pieces
            tp = (net_operating_time / actual_operating_time) * 100 if actual_operating_time > 0 else 0.0
        else:
            tp = 0.0
            
        # 3. TQ (Quality)
        # Ratio of Good Pieces / Total Pieces
        tq = (good_pieces / total_pieces) * 100 if total_pieces > 0 else 0.0
        
        # 4. TRS (Overall Equipment Effectiveness)
        # TRS = TDO * TP * TQ
        trs = (tdo / 100.0) * (tp / 100.0) * (tq / 100.0) * 100
        
        # Cap values at 100% and 0%
        tdo = max(0.0, min(100.0, tdo))
        tp = max(0.0, min(100.0, tp))
        tq = max(0.0, min(100.0, tq))
        trs = max(0.0, min(100.0, trs))

        # Update machine cache
        machine.tdo = round(tdo, 1)
        machine.tp = round(tp, 1)
        machine.tq = round(tq, 1)
        machine.trs = round(trs, 1)
        
        # Save snapshot
        snapshot = KpiSnapshot(
            machine_id=machine.id,
            trs=machine.trs,
            tdo=machine.tdo,
            tp=machine.tp,
            tq=machine.tq,
            recorded_at=now
        )
        db.session.add(snapshot)

    db.session.commit()
    print(f"[{now}] KPI calculation complete for {len(machines)} machines.")
