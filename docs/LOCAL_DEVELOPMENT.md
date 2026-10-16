# Local Development

This document explains how to run and test the Step 6 ReleaseGuard application locally. PostgreSQL temporarily runs in Docker; full application containerization and Docker Compose will be added in Step 7.

## Why the project has two applications

- `backend/` is the FastAPI service. It owns validation, business rules, persistence, and operational endpoints.
- `frontend/` is the React application. It owns the user interface and calls the backend over HTTP.
- Keeping them separate lets CI test, scan, build, and deploy each component independently.

## Runtime versions

- Python 3.12 is recorded in `.python-version`.
- Node.js 22 is recorded in `.nvmrc` and will also be used by CI and Docker.
- A local Node version newer than 22 can be used when it satisfies the package engine requirements, but Node 22 is the reproducible project baseline.

## Run PostgreSQL

Create the development database once:

```bash
docker run --name releaseguard-postgres-dev \
  --env POSTGRES_DB=releaseguard \
  --env POSTGRES_USER=releaseguard \
  --env POSTGRES_PASSWORD=CHANGE_ME_LOCAL_ONLY \
  --publish 127.0.0.1:5432:5432 \
  --volume releaseguard-postgres-data:/var/lib/postgresql/data \
  --detach postgres:17-alpine
```

Replace `CHANGE_ME_LOCAL_ONLY` with a password used only on your laptop, and place the same value in your ignored `backend/.env`. Production credentials will come from Kubernetes Secrets and will never be committed.

On later days, start the existing container with:

```bash
docker start releaseguard-postgres-dev
```

## Run the backend

From the repository root:

```bash
python3.12 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.lock.txt
cd backend
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Useful URLs:

- API root: `http://localhost:8000/`
- Liveness: `http://localhost:8000/health`
- Readiness: `http://localhost:8000/ready`
- Interactive OpenAPI documentation: `http://localhost:8000/docs`

`/health` answers whether the API process is alive. `/ready` checks both the API and PostgreSQL, so Kubernetes will not send traffic to an instance that cannot access its required database.

The release API is available below `/api/releases`. Use `http://localhost:8000/docs` to create records and explore the generated request and response schemas without writing curl commands.

## Database migrations

Alembic changes the database schema in reviewable, versioned steps. Apply committed migrations with:

```bash
cd backend
.venv/bin/alembic upgrade head
```

Check that the SQLAlchemy models and migrated database have not drifted apart:

```bash
.venv/bin/alembic check
```

The application never creates production tables automatically at startup. Explicit migrations make schema changes visible in code review and repeatable in CI/CD.

## Run the automated tests

Create a separate test database once while the development PostgreSQL container is running:

```bash
docker exec releaseguard-postgres-dev \
  createdb --username releaseguard releaseguard_test
```

If PostgreSQL says the database already exists, no action is needed. Install the test dependency lock and run the suite from `backend/`:

```bash
cd backend
.venv/bin/python -m pip install -r requirements-dev.lock.txt
export RELEASEGUARD_TEST_DATABASE_URL='postgresql+psycopg://releaseguard:CHANGE_ME_LOCAL_ONLY@localhost:5432/releaseguard_test'
.venv/bin/python -m pytest
```

Replace `CHANGE_ME_LOCAL_ONLY` with the same local-only password used by the PostgreSQL container. Do not save the real value in a tracked file.

The suite has three complementary layers:

- `tests/test_readiness.py` tests scoring and risk rules as fast, database-free unit tests.
- `tests/test_releases_api.py` sends real HTTP requests through FastAPI and verifies validation, CRUD, filtering, lifecycle rules, readiness, and statistics.
- `tests/test_system_api.py` verifies liveness/readiness behavior, including the database-unavailable failure path.

The fixtures reject any database whose name does not end in `_test`. They create the schema once and wrap each test in a database transaction that is rolled back afterward. This gives each test clean data without touching the development database.

Coverage measures which application statements and decision branches the tests execute. `pyproject.toml` makes the command fail below 90%, turning coverage into an enforceable quality gate rather than an optional report.

## Run the frontend

In a second terminal, from the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. The status card calls the backend `/health` endpoint, proving the two applications can communicate.

The Step 6 interface now provides the complete application workflow: dashboard statistics, server-backed search and filters, release creation and editing, readiness evidence controls, detail inspection, allowed lifecycle actions, and draft deletion. See [FRONTEND.md](FRONTEND.md) for the data flow and component responsibilities.

## Environment files

Copy the example files only when a local override is required:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

The backend database URL is required, so copy its example before starting the API and replace the password placeholder. Real `.env` files are ignored by Git because they can contain credentials. Example files are committed because they document required variable names without containing secrets.

## Why dependency intent and lock files are separate

- `backend/requirements.txt` lists the Python packages we intentionally chose.
- `backend/requirements.lock.txt` records the exact resolved Python package tree used by automation.
- `backend/requirements-dev.txt` adds packages used only for tests and coverage.
- `backend/requirements-dev.lock.txt` pins the complete test environment used locally and in CI.
- `frontend/package.json` lists the JavaScript packages we intentionally chose.
- `frontend/package-lock.json` records the exact resolved JavaScript package tree used by `npm ci`.

This gives humans a short dependency list while still giving CI and containers deterministic installations.
