# 🔄 Migration Guide: Monolith → Microservices (trs-platform)

## Overview

You're migrating from a **single Flask monolith** (`trs_digitalisation/`) to a **microservices architecture** (`trs-platform/`). This document maps **every file** from the old project to its new location and explains exactly what changes.

---

## 🧠 Architecture Comparison

```
BEFORE (Monolith):                    AFTER (Microservices):
┌────────────────────┐                ┌──────────────────────────────────┐
│  Single Flask App  │                │  ingestion-service (Flask)       │
│  ├── models.py     │                │  kpi-service (standalone Python) │
│  ├── routes/api.py │    ──────►     │  dashboard-service (Flask)       │
│  ├── routes/auth.py│                │  raw-data-generator (Python)     │
│  ├── templates/    │                │  Node-RED + MQTT (Docker)        │
│  └── static/       │                └──────────────────────────────────┘
└────────────────────┘
```

---

## 📋 Complete File-by-File Migration Map

### Legend

- ✅ **COPY AS-IS** — take directly, no changes needed
- 🔧 **COPY + MODIFY** — take the file but adapt it  
- 🆕 **CREATE NEW** — doesn't exist in old project, must be written from scratch
- ❌ **DROP** — not needed in new architecture

---

## 🟢 1. `services/ingestion-service/`

> **Role**: Receives events from Node-RED, validates, enriches, stores in DB

### File Mapping

| New File | Source from Old Project | Action | Changes Needed |
|---|---|---|---|
| `app/__init__.py` | — | 🆕 | Empty file |
| `app/config.py` | [config.py](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/config.py) | 🔧 | Remove `SECRET_KEY`, `SQLALCHEMY_TRACK_MODIFICATIONS`. Keep `DATABASE_URL` and `API_KEY` only |
| `app/db.py` | [extensions.py](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/extensions.py) | 🔧 | Same concept — `db = SQLAlchemy()`. Rename file from `extensions.py` to `db.py` |
| `app/routes/ingest.py` | [api.py lines 313-355](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/routes/api.py#L313-L355) | 🔧 | Take the `/api/ingest/machine/<id>` endpoint. Change it to just `POST /ingest`. See details below |
| `app/routes/clients.py` | — | 🆕 | CRUD for clients (optional — only if ingestion needs client management) |
| `app/routes/factories.py` | — | 🆕 | CRUD for usines/factories |
| `app/routes/machines.py` | [api.py lines 139-200](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/routes/api.py#L139-L200) | 🔧 | Take machine CRUD (add/update/delete). Remove `require_login` decorator. Use API key auth instead |
| `app/services/event_service.py` | — | 🆕 | Extract the ingest logic from the route into a service class |
| `app/services/machine_service.py` | — | 🆕 | Extract machine logic, add `device_id` generation |
| `run.py` | [app.py](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/app.py) | 🔧 | Simplified entry point. Only registers ingestion-related blueprints |
| `requirements.txt` | — | 🆕 | `flask`, `flask-sqlalchemy`, `psycopg2-binary`, `python-dotenv` |
| `Dockerfile` | — | 🆕 | Standard Python Docker image |

### 🔥 Key Changes for `ingest.py`

Your current ingest endpoint (`/api/ingest/machine/<machine_id>`) receives **already-computed TRS values**. In the new architecture, it will receive **events** from Node-RED instead:

```python
# OLD (current) — receives computed KPIs directly:
machine.trs = data.get("trs", machine.trs)
machine.tdo = data.get("tdo", machine.tdo)

# NEW — receives events (piece_detected, machine_state, classification):
# POST /ingest
# {
#   "device_id": "raspi_001",
#   "event_type": "piece_detected" | "machine_state" | "classification",
#   "data": { ... },
#   "timestamp": 1710000000
# }
```

> [!IMPORTANT]
> The ingestion service **no longer computes KPIs**. It only validates events and stores them. The KPI service handles all calculations.

### 🔥 Key Change: New `events` Table

You need a new model that doesn't exist in the current project:

```python
class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machines.id"), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # piece_detected, machine_state, classification
    data = db.Column(db.JSON)  # raw event data
    timestamp = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 🔵 2. `services/kpi-service/`

> **Role**: Reads events, computes TRS/TDO/TP/TQ, stores results

### File Mapping

| New File | Source from Old Project | Action | Changes Needed |
|---|---|---|---|
| `app/db.py` | [extensions.py](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/extensions.py) | 🔧 | DB connection (same pattern) |
| `app/queries.py` | — | 🆕 | SQL queries to fetch events by time window, fetch machines |
| `app/kpi_engine.py` | — | 🆕 | **Core math**: count pieces, detect downtime, calculate TRS/TDO/TP/TQ |
| `app/scheduler.py` | — | 🆕 | Loop every X seconds → fetch events → compute KPIs → store |
| `app/main.py` | — | 🆕 | Entry point that starts the scheduler |
| `requirements.txt` | — | 🆕 | `sqlalchemy`, `psycopg2-binary`, `python-dotenv`, `schedule` or `APScheduler` |
| `Dockerfile` | — | 🆕 | Standard Python Docker image |

> [!NOTE]  
> The KPI engine is **entirely new**. In your current project, TRS values are pushed directly by Node-RED into the ingest endpoint. In the new architecture, raw events are stored first, then the KPI service reads them and calculates everything.

### 🔥 KPI Engine Logic (New)

```python
# What kpi_engine.py should compute:
# 
# 1. TDO (Taux de Disponibilité / Availability):
#    = Temps de fonctionnement / Temps requis
#    Use machine_state events to detect running vs downtime
#
# 2. TP (Taux de Performance / Performance):
#    = (Nombre de pièces × Temps de cycle théorique) / Temps de fonctionnement
#    Use piece_detected events + machine's cadence_theorique
#
# 3. TQ (Taux de Qualité / Quality):
#    = Pièces bonnes / Pièces totales
#    Use classification events (good vs defect)
#
# 4. TRS = TDO × TP × TQ
```

---

## 🟣 3. `services/dashboard-service/` ⭐ (YOUR DASHBOARD STAYS THE SAME)

> **Role**: Serves the web UI — templates, static files, and API endpoints for the frontend

### File Mapping

| New File | Source from Old Project | Action | Changes Needed |
|---|---|---|---|
| **BACKEND** | | | |
| `app/__init__.py` | — | 🆕 | Empty |
| `app/routes/dashboard.py` | [api.py lines 21-65](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/routes/api.py#L21-L65) + [api.py lines 241-290](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/routes/api.py#L241-L290) + [pages.py](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/routes/pages.py) | 🔧 | Combine page routes + data API routes. See details below |
| `app/routes/auth.py` | [auth.py](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/routes/auth.py) | ✅ | **Copy as-is** (login, register, logout) |
| `run.py` | [app.py](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/app.py) | 🔧 | Only registers dashboard + auth blueprints |
| **TEMPLATES** | | | |
| `app/templates/base.html` | [base.html](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/templates/base.html) | ✅ | **Copy as-is** |
| `app/templates/dashboard.html` | [dashboard.html](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/templates/dashboard.html) | ✅ | **Copy as-is** |
| `app/templates/machine.html` | [machine.html](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/templates/machine.html) | ✅ | **Copy as-is** |
| `app/templates/analysis.html` | [analysis.html](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/templates/analysis.html) | ✅ | **Copy as-is** |
| `app/templates/settings.html` | [settings.html](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/templates/settings.html) | ✅ | **Copy as-is** |
| `app/templates/profile.html` | [profile.html](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/templates/profile.html) | ✅ | **Copy as-is** |
| `app/templates/login.html` | [login.html](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/templates/login.html) | ✅ | **Copy as-is** |
| `app/templates/usine.html` | [usine.html](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/templates/usine.html) | ✅ | **Copy as-is** |
| **CSS** | | | |
| `app/static/css/base.css` | [base.css](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/static/css/base.css) | ✅ | **Copy as-is** |
| `app/static/css/dashboard.css` | [dashboard.css](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/static/css/dashboard.css) | ✅ | **Copy as-is** |
| `app/static/css/machine.css` | [machine.css](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/static/css/machine.css) | ✅ | **Copy as-is** |
| `app/static/css/analysis.css` | [analysis.css](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/static/css/analysis.css) | ✅ | **Copy as-is** |
| `app/static/css/settings.css` | [settings.css](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/static/css/settings.css) | ✅ | **Copy as-is** |
| `app/static/css/profile.css` | [profile.css](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/static/css/profile.css) | ✅ | **Copy as-is** |
| **JAVASCRIPT** | | | |
| `app/static/js/base.js` | [base.js](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/static/js/base.js) | ✅ | **Copy as-is** |
| `app/static/js/dashboard.js` | [dashboard.js](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/static/js/dashboard.js) | 🔧 | **API URL change only** (see below) |
| `app/static/js/machine.js` | [machine.js](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/static/js/machine.js) | 🔧 | **API URL change only** + remove mock data handling |
| `app/static/js/analysis.js` | [analysis.js](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/static/js/analysis.js) | 🔧 | **API URL change only** |
| `app/static/js/settings.js` | [settings.js](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/static/js/settings.js) | 🔧 | **API URL change only** |
| `app/static/js/profile.js` | [profile.js](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/static/js/profile.js) | ✅ | **Copy as-is** |
| **OTHER** | | | |
| `requirements.txt` | — | 🆕 | `flask`, `flask-sqlalchemy`, `psycopg2-binary`, `python-dotenv` |
| `Dockerfile` | — | 🆕 | Standard Python Docker image |

### 🔧 JavaScript API URL Changes

Since the dashboard is now a **separate service**, and the CRUD APIs for usines/machines now live in the **ingestion-service**, the JS files need to point to the right service.

**Option A (Simple — recommended for now)**: Keep all API endpoints in the dashboard service itself (since it connects to the same DB). This means **NO JS changes at all**. The dashboard-service keeps its own `/api/` routes.

**Option B (Pure microservices)**: Dashboard JS calls the ingestion-service API directly. This requires CORS setup and URL changes in all JS files.

> [!IMPORTANT]
> **I recommend Option A for your project.** The dashboard-service keeps its own API routes that read from the shared database. This is simpler, avoids CORS issues, and your frontend JS stays exactly the same. The only thing that changes is: **the dashboard no longer has the `/api/ingest` endpoint** — that moves to ingestion-service.

### What stays in `dashboard-service/routes/dashboard.py`

From [api.py](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/routes/api.py):

```
✅ KEEP: GET /api/dashboard-data      (lines 21-65)
✅ KEEP: GET /api/usines               (lines 70-92)
✅ KEEP: POST /api/usines              (lines 95-109)
✅ KEEP: PUT /api/usines/<id>          (lines 112-125)
✅ KEEP: DELETE /api/usines/<id>       (lines 128-136)
✅ KEEP: POST /api/usines/<id>/machines (lines 141-165)
✅ KEEP: PUT /api/machines/<id>        (lines 168-187)
✅ KEEP: DELETE /api/machines/<id>     (lines 190-200)
✅ KEEP: GET /api/machines/<id>/details (lines 203-239)
✅ KEEP: GET /api/machines/<id>/history (lines 243-266)
✅ KEEP: GET /api/all-machines-history  (lines 269-290)
✅ KEEP: PUT /api/profile              (lines 295-310)

❌ REMOVE: POST /api/ingest/machine/<id>  → moves to ingestion-service
❌ REMOVE: POST /api/trs (legacy)         → not needed
```

### What changes in `machine.js`

The `mock_live_data` section (random data for temperature, vibration, etc.) will eventually be replaced by **real data** from the events table. For now, you can keep the mock or change the details endpoint to read real events from the DB.

---

## 🟡 4. `simulations/raw-data-generator/`

> **Role**: Simulates industrial sensors, publishes to MQTT

### File Mapping

| New File | Source from Old Project | Action | Changes Needed |
|---|---|---|---|
| `main.py` | — | 🆕 | Orchestrator: loops machines, calls generators, publishes to MQTT |
| `generators/vibration.py` | — | 🆕 | Simulates vibration values (normal + spike for downtime) |
| `generators/distance.py` | — | 🆕 | Simulates distance sensor (piece passing detection) |
| `generators/camera.py` | — | 🆕 | Simulates camera classification (good/defect with probability) |
| `config.py` | — | 🆕 | MQTT broker URL, simulation speed, machine configs |
| `requirements.txt` | — | 🆕 | `paho-mqtt`, `python-dotenv` |
| `Dockerfile` | — | 🆕 | Standard Python Docker image |

> [!NOTE]
> Nothing from the old project maps here. The old project has `seed_demo_history()` in [helpers.py](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/helpers.py) which generates fake TRS history — but the simulation service is completely different. It generates **raw sensor data**, not pre-computed KPIs.

---

## 🟠 5. `infrastructure/`

> **Role**: Docker orchestration, Node-RED flows, MQTT broker

### File Mapping

| New File | Source from Old Project | Action | Changes Needed |
|---|---|---|---|
| `node-red/flows.json` | — | 🆕 | MQTT IN → Function nodes → HTTP POST to ingestion |
| `mqtt/mosquitto.conf` | — | 🆕 | Basic Mosquitto config |
| `docker-compose.yml` | — | 🆕 | Defines all 6 services (mqtt, node-red, ingestion, kpi, dashboard, simulation) |

---

## 🟣 6. `shared/`

> **Role**: Reusable code shared between services

### File Mapping

| New File | Source from Old Project | Action | Changes Needed |
|---|---|---|---|
| `models/client.py` | [models.py lines 10-26](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/models.py#L10-L26) | 🔧 | Extract `Client` class |
| `models/usine.py` | [models.py lines 28-42](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/models.py#L28-L42) | 🔧 | Extract `Usine` class (rename to `Factory` optionally) |
| `models/machine.py` | [models.py lines 45-71](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/models.py#L45-L71) | 🔧 | Extract `Machine` class. Add `device_id` field |
| `models/event.py` | — | 🆕 | New `Event` model (doesn't exist in old project) |
| `models/trs_history.py` | [models.py lines 74-85](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/models.py#L74-L85) | 🔧 | Extract `TrsHistory` class |
| `utils/logging.py` | — | 🆕 | Shared logging config |
| `utils/constants.py` | — | 🆕 | Event types: `PIECE_DETECTED`, `MACHINE_STATE`, `CLASSIFICATION` |
| `utils/dates.py` | — | 🆕 | Date helpers |

### 🔥 Changes to Machine Model

```python
# OLD (current):
class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usine_id = db.Column(...)
    nom = db.Column(...)
    # ... etc

# NEW — add device_id:
class Machine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usine_id = db.Column(...)
    nom = db.Column(...)
    device_id = db.Column(db.String(100), unique=True)  # 🆕 links to physical Raspberry Pi
    # ... rest stays the same
```

---

## ❌ Files NOT Needed in New Architecture

| Old File | Reason |
|---|---|
| [helpers.py](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/helpers.py) → `seed_demo_history()` | Replaced by simulation service. `require_login` and `get_current_client` → move to dashboard-service |
| [helpers.py](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/helpers.py) → `require_login()` | Move to `dashboard-service` only |
| [migrate_db.py](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/migrate_db.py) | Use proper migration tool (Alembic) or let `db.create_all()` handle it |
| [routes/**init**.py](file:///c:/Users/user/Desktop/pfa%20backend/trs_digitalisation/routes/__init__.py) | Replaced by per-service route files |

---

## 📊 Visual Summary: What Goes Where

```
OLD PROJECT (monolith)              →  NEW PROJECT (microservices)
═══════════════════════════════════════════════════════════════════

config.py                           →  ingestion-service/app/config.py  🔧
                                    →  kpi-service/app/config.py        🔧
                                    →  dashboard-service/app/config.py  🔧

extensions.py (db)                  →  shared pattern in each service's db.py

models.py (Client)                  →  shared/models/client.py
models.py (Usine)                   →  shared/models/usine.py
models.py (Machine)                 →  shared/models/machine.py  (+ device_id)
models.py (TrsHistory)              →  shared/models/trs_history.py
                                    →  shared/models/event.py  🆕

routes/api.py (ingest endpoint)     →  ingestion-service/app/routes/ingest.py  🔧
routes/api.py (machine CRUD)        →  dashboard-service/app/routes/dashboard.py
routes/api.py (usine CRUD)          →  dashboard-service/app/routes/dashboard.py
routes/api.py (dashboard-data)      →  dashboard-service/app/routes/dashboard.py
routes/api.py (history endpoints)   →  dashboard-service/app/routes/dashboard.py
routes/api.py (profile)             →  dashboard-service/app/routes/dashboard.py
routes/auth.py                      →  dashboard-service/app/routes/auth.py  ✅
routes/pages.py                     →  dashboard-service/app/routes/dashboard.py  ✅

templates/* (ALL 8 files)           →  dashboard-service/app/templates/*  ✅
static/css/* (ALL 6 files)          →  dashboard-service/app/static/css/*  ✅
static/js/* (ALL 6 files)           →  dashboard-service/app/static/js/*  ✅

helpers.py (require_login)          →  dashboard-service/app/helpers.py
helpers.py (seed_demo_history)      →  ❌ DROP (replaced by simulation)

app.py                              →  dashboard-service/run.py  🔧

.env                                →  trs-platform/.env  🔧 (add MQTT vars)
```

---

## 🔥 Summary of What's NEW (doesn't exist in current project)

1. **`Event` model** — raw events from sensors (piece, machine state, quality)
2. **`device_id` on Machine** — links software machine to physical Raspberry Pi
3. **KPI Engine** — all TRS/TDO/TP/TQ math (currently non-existent, values were pushed directly)
4. **KPI Scheduler** — periodic loop that computes KPIs
5. **MQTT integration** — simulation publishes to MQTT topics
6. **Node-RED flows** — MQTT → event processing → HTTP ingestion
7. **Docker Compose** — orchestrates all services together
8. **Simulation generators** — vibration, distance, camera simulators

## 🔥 Summary of What STAYS THE SAME

1. **All HTML templates** (8 files) — ✅ copy as-is
2. **All CSS files** (6 files) — ✅ copy as-is
3. **All JS files** (6 files) — ✅ copy as-is (with Option A, no URL changes needed)
4. **Auth routes** (login/register/logout) — ✅ copy as-is
5. **All DB models** (Client, Usine, Machine, TrsHistory) — ✅ copy with minor additions
6. **Dashboard API endpoints** — ✅ stay in dashboard-service
7. **Same Supabase database** — ✅ all services connect to the same DB

---

## 🚀 Recommended Build Order

| Step | What | Time |
|---|---|---|
| 1 | Set up `shared/models/` — copy all models + add Event | 30 min |
| 2 | Set up `ingestion-service` — config, db, ingest route | 1-2 hours |
| 3 | Test ingestion with Postman | 15 min |
| 4 | Set up `dashboard-service` — copy ALL frontend + API routes | 1 hour |
| 5 | Verify dashboard works identically | 30 min |
| 6 | Set up MQTT + Docker Compose | 1 hour |
| 7 | Set up Node-RED flows | 1-2 hours |
| 8 | Set up simulation service | 1-2 hours |
| 9 | Set up KPI service | 2-3 hours |
| 10 | End-to-end test | 1 hour |

---

## Open Questions

> [!IMPORTANT]
> **Question 1**: For the dashboard, do you want **Option A** (dashboard keeps its own API routes → zero JS changes) or **Option B** (JS calls ingestion-service directly → requires CORS + URL changes)?  
> I strongly recommend **Option A**.

> [!IMPORTANT]  
> **Question 2**: Where is your new `trs-platform` project folder located? I need the path to help you set up files there if you want.

> [!WARNING]
> **Question 3**: Your `.env` currently has your Supabase credentials in plain text. In the new architecture with Docker, these will be shared via the root `.env` file. Make sure to add `.env` to `.gitignore` in the new project.
