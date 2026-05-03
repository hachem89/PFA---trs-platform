# KPI Calculation Service Implementation (Updated)

This plan adapts to the existing file structure found in `services/kpi-service/`. We will transform the empty skeleton into a fully functional industrial analytics engine.

## User Review Required

> [!IMPORTANT]
> **Existing Structure**: I will utilize the `app/` folder structure you created, specifically using `kpi_engine.py` for the core math and `scheduler.py` for the timing logic.
>
> **Look-back Logic**: To handle machines running across window boundaries (e.g., started at 09:55, still running at 10:05), we will query the last state before the window starts.

## Proposed Changes

### [KPI Service] (services/kpi-service/)

#### [MODIFY] [kpi_engine.py](file:///c:/Users/user/Desktop/PFA%20-%20trs%20platform/services/kpi-service/app/kpi_engine.py)
This will host the `calculate_window_kpis` function using the **Instantaneous (Option B)** approach:
- **TDO** (Availability) = `runtime_in_window / 300` (window duration in seconds).
- **TP** (Performance) = `(theoretical_cycle_time * total_pieces) / runtime_in_window`.
- **TQ** (Quality) = `good_pieces / total_pieces`.
- **TRS** = `TDO * TP * TQ`.
- *Note*: If `runtime_in_window` is 0, `TP` will be 0 to avoid division by zero.

#### [MODIFY] [scheduler.py](file:///c:/Users/user/Desktop/PFA%20-%20trs%20platform/services/kpi-service/app/scheduler.py)
The background loop:
- Calculates the delay to align with 5-minute boundaries (00, 05, 10...).
- Iterates through all machines in the database.
- Triggers the engine and saves a `KpiSnapshot` for each machine.

#### [MODIFY] [queries.py](file:///c:/Users/user/Desktop/PFA%20-%20trs%20platform/services/kpi-service/app/queries.py)
Database extraction helpers:
- `get_window_events(machine_id, start, end)`: Fetches pieces, states, and classifications.
- `get_last_state_before(machine_id, start)`: The "look-back" query for runtime continuity.

#### [NEW] [run.py](file:///c:/Users/user/Desktop/PFA%20-%20trs%20platform/services/kpi-service/run.py)
The entry point at the root of the service.
- Initializes the Flask App.
- Starts the `scheduler` thread.
- Runs the server on port 5002.

---

### [Infrastructure]

#### [MODIFY] [docker-compose.yaml](file:///c:/Users/user/Desktop/PFA%20-%20trs%20platform/infrastructure/docker-compose.yaml)
- Add `kpi-service`.
- Map the global `.env` for database access.
- Use `..` as context to allow importing the `shared/` models.

## Verification Plan

### Manual Verification
1. **Startup Alignment**: Check logs for: `[KPI] Next execution scheduled for 10:45:00`.
2. **Snapshot Accuracy**:
    - Add a machine → Check if snapshots appear every 5 mins.
    - Check columns in `kpi_snapshots`: `trs`, `tdo`, `tp`, `tq` should be between 0 and 100.
3. **Resilience**: Stop the `simulation` service and verify that the next snapshot for the machine shows 0% Performance and reduced Availability.
