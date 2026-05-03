import logging
from flask import Blueprint, jsonify

kpi_engine_bp = Blueprint('kpi_engine', __name__)

@kpi_engine_bp.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "kpi-service"})

logger = logging.getLogger(__name__)

def calculate_window_kpis(machine, events, initial_state, start_time, end_time):
    """
    Core math engine for a 5-minute tumbling window.
    Formula approach: Instantaneous (Option B).
    """
    total_pieces = 0
    good_pieces = 0
    defective_pieces = 0
    runtime_seconds = 0.0
    
    current_state = initial_state
    last_ts = start_time
    
    for event in events:
        if current_state == 'running':
            duration = (event.timestamp - last_ts).total_seconds()
            runtime_seconds += max(0, duration)
        
        if event.event_type == 'piece_detected':
            total_pieces += 1
        elif event.event_type == 'classification':
            if event.value == 'good':
                good_pieces += 1
            else:
                defective_pieces += 1
        elif event.event_type == 'machine_state':
            current_state = event.value
            
        last_ts = event.timestamp
    
    if current_state == 'running':
        duration = (end_time - last_ts).total_seconds()
        runtime_seconds += max(0, duration)
    
    window_duration = (end_time - start_time).total_seconds()
    
    tdo = (runtime_seconds / window_duration) * 100 if window_duration > 0 else 0
    tq = (good_pieces / total_pieces) * 100 if total_pieces > 0 else 0
    
    tc = machine.theoretical_cycle_time or 1.0
    if runtime_seconds > 0:
        tp = ((tc * total_pieces) / runtime_seconds) * 100
    else:
        tp = 0.0
        
    tp = min(tp, 100.0)
    trs = (tdo / 100) * (tp / 100) * (tq / 100) * 100
    
    result = {
        "trs": round(trs, 2),
        "tdo": round(tdo, 2),
        "tp": round(tp, 2),
        "tq": round(tq, 2),
        "total_pieces": total_pieces,
        "good_pieces": good_pieces,
        "defective_pieces": defective_pieces,
        "runtime_seconds": round(runtime_seconds, 1)
    }
    
    logger.info(f"Machine {machine.name}: {result}")
    return result
