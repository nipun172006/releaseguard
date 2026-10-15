# Local Development

This document explains how to run the Step 3 ReleaseGuard foundation without Docker. Dockerized development will be added in Step 7.

## Why the project has two applications

- `backend/` is the FastAPI service. It owns validation, business rules, persistence, and operational endpoints.
- `frontend/` is the React application. It owns the user interface and calls the backend over HTTP.
- Keeping them separate lets CI test, scan, build, and deploy each component independently.

## Runtime versions

- Python 3.12 is recorded in `.python-version`.
- Node.js 22 is recorded in `.nvmrc` and will also be used by CI and Docker.
- A local Node version newer than 22 can be used when it satisfies the package engine requirements, but Node 22 is the reproducible project baseline.

## Run the backend

From the repository root:

```bash
python3.12 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.lock.txt
cd backend
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Useful URLs:

- API root: `http://localhost:8000/`
- Liveness: `http://localhost:8000/health`
- Readiness: `http://localhost:8000/ready`
- Interactive OpenAPI documentation: `http://localhost:8000/docs`

`/health` answers whether the API process is alive. `/ready` will become stricter in Step 4 and check whether PostgreSQL is reachable before Kubernetes sends traffic to the API.

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

Real `.env` files are ignored by Git because they can contain credentials. Example files are committed because they document required variable names without containing secrets.

## Why there are two dependency files per ecosystem

- `backend/requirements.txt` lists the Python packages we intentionally chose.
- `backend/requirements.lock.txt` records the exact resolved Python package tree used by automation.
- `frontend/package.json` lists the JavaScript packages we intentionally chose.
- `frontend/package-lock.json` records the exact resolved JavaScript package tree used by `npm ci`.

This gives humans a short dependency list while still giving CI and containers deterministic installations.
