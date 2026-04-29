# Dashboard Service Migration Plan

This document outlines the step-by-step strategy to migrate the old monolithic dashboard into the new `dashboard-service` architecture. As requested, we will prioritize migrating the UI/UX **first** with absolutely zero design changes, verifying it, and then moving to the backend logic (Auth, CRUD, APIs).

## User Review Required

> [!IMPORTANT]
> You were absolutely right! I had originally missed the bottom half of the files. I have now read all 1999 lines of the UI code and 1712 lines of the old project code. I've updated the plan below to map **every single file** accurately. Please review and approve!

## Open Questions

> [!NOTE]
> 1. Do you want me to write the Python scripts to auto-extract the HTML/CSS from `ui_code.md` for you, or do you prefer to copy-paste them manually as I guide you? (I can fully automate the extraction if you'd like).
> 2. Currently, `older project.md` uses Flask session cookies for auth. Is it okay to keep using session cookies for the `dashboard-service` since it renders the HTML directly?

---

## Proposed Changes & Todo List

### Phase 1: Setup & UI Migration (Zero Design Changes)
*Objective: Get the UI up and running locally to visually verify it matches the old layout.*

- [ ] **Create Directory Structure**: 
  - `services/dashboard-service/app/static/css/`
  - `services/dashboard-service/app/static/js/`
  - `services/dashboard-service/app/templates/`
  - `services/dashboard-service/app/routes/`
- [ ] **Migrate CSS Files**: Extract the following from `ui_code.md` into `static/css/`:
  - `analysis.css`, `base.css`, `dashboard.css`, `machine.css`, `profile.css`, `settings.css`.
- [ ] **Migrate JS Files**: Extract the following from `ui_code.md` into `static/js/`:
  - `analysis.js` (Chart.js logic), `base.js` (Sidebar & gauges), `dashboard.js` (Live dashboard), `machine.js` (Machine details), `profile.js` (Settings update), `settings.js` (CRUD modal logic).
- [ ] **Migrate HTML Templates**: Extract the following from `ui_code.md` into `templates/`:
  - `analysis.html`, `base.html`, `dashboard.html`, `login.html`, `machine.html`, `profile.html`, `settings.html`, `usine.html`.
- [ ] **Setup Flask Shell**: 
  - Create `services/dashboard-service/app/__init__.py` and `services/dashboard-service/run.py`.
  - Create a temporary dummy route to render the login page just to verify CSS/HTML is loading correctly without DB errors.

### Phase 2: Authentication (Login, Register, Logout)
*Objective: Make the login and registration forms fully functional with the new `shared.models` database.*

- [ ] **Setup Database Connection**: Update `services/dashboard-service/app/config.py` and `__init__.py` to initialize SQLAlchemy.
- [ ] **Migrate Helpers**: Copy `helpers.py` (specifically `require_login`, `get_current_client`, and `seed_demo_history`) into `app/helpers.py`.
- [ ] **Migrate Auth Routes**: Copy `routes/auth.py` from `older project.md` to `app/routes/auth.py` (handles `/login`, `/register`, `/logout`).
- [ ] **Refactor Imports**: Update `models.py` imports in `auth.py` to point to `shared.models.client.Client`, `shared.models.usine.Usine`, and `shared.models.machine.Machine`.

### Phase 3: APIs and Dashboard Data (CRUD)
*Objective: Populate the dashboard with real database data instead of loaders.*

- [ ] **Migrate Page Routes**: Extract `routes/pages.py` to `app/routes/pages.py` to handle the standard URL routing (`/dashboard`, `/analysis`, `/settings`, `/profile`, `/machine/<id>`).
- [ ] **Migrate API Routes**: Extract `routes/api.py` to `app/routes/api.py`.
  - *Crucial Change*: We will **REMOVE** the `/ingest/machine/<int:machine_id>` and `/trs` endpoints from here, as they are now handled exclusively by the new `ingestion-service`!
  - Keep endpoints: `/dashboard-data`, `/usines` (GET/POST/PUT/DELETE), `/machines` (POST/PUT/DELETE), `/machines/<id>/details`, `/machines/<id>/history`, and `/profile`.
- [ ] **Refactor Imports**: Ensure all DB interactions in `api.py` and `pages.py` use the new `shared.models` package.

### Phase 4: Dockerization & Deployment
*Objective: Prepare the dashboard for production deployment alongside the ingestion-service.*

- [ ] **Create Requirements**: Create `services/dashboard-service/requirements.txt` (including `Flask`, `gunicorn`, `SQLAlchemy`, `python-dotenv`, `psycopg2-binary`).
- [ ] **Create Dockerfile**: Create `services/dashboard-service/Dockerfile` using Gunicorn (`CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]`).
- [ ] **Update Docker Compose**: Add `dashboard-service` to `infrastructure/docker-compose.yaml`, map port `5001:5000`, and connect it to the `infrastructure_default` network so it shares the Postgres DB.

## Verification Plan

### Manual Verification
1. **Visual Check**: We will run the Flask app locally in Phase 1 and visually inspect the login page and dashboard to ensure no CSS/JS was lost.
2. **Auth Check**: Register a new user, log in, and ensure the session is maintained.
3. **Data Check**: Add a new machine via the `settings` UI and verify it persists in the shared Postgres DB.
4. **Integration Check**: We will spin up `docker-compose up` and verify Node-RED sends data to `ingestion-service`, and that data instantly reflects on the `dashboard-service` UI via the database.
