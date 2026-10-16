# Local Development

This document explains how to run the Step 4 ReleaseGuard application locally. PostgreSQL temporarily runs in Docker; full application containerization and Docker Compose will be added in Step 7.

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

## Run the frontend

In a second terminal, from the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. The status card calls the backend `/health` endpoint, proving the two applications can communicate.

## Environment files

Copy the example files only when a local override is required:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

The backend database URL is required, so copy its example before starting the API and replace the password placeholder. Real `.env` files are ignored by Git because they can contain credentials. Example files are committed because they document required variable names without containing secrets.

## Why there are two dependency files per ecosystem

- `backend/requirements.txt` lists the Python packages we intentionally chose.
- `backend/requirements.lock.txt` records the exact resolved Python package tree used by automation.
- `frontend/package.json` lists the JavaScript packages we intentionally chose.
- `frontend/package-lock.json` records the exact resolved JavaScript package tree used by `npm ci`.

This gives humans a short dependency list while still giving CI and containers deterministic installations.
