# Docker and Local Stack

Step 7 packages ReleaseGuard into the same style of immutable application images that CI and Kubernetes will use later. Docker Compose connects those images to PostgreSQL for a repeatable local environment.

## Architecture

```text
Browser
  |
  | http://localhost:5173
  v
Nginx frontend container (non-root, port 8080)
  |-- static React assets
  `-- /api, /health, /ready, /docs proxy
              |
              v
       FastAPI container (non-root, port 8000)
              |
              v
       PostgreSQL container (internal port 5432)
              |
              v
       named volume: postgres-data
```

Only the frontend and backend are bound to `127.0.0.1`. PostgreSQL is reachable only from the private Compose network. The browser calls Nginx on one origin, and Nginx forwards API paths internally to `backend:8000`.

## Container files

- `backend/Dockerfile` creates a virtual environment in a builder stage and copies only the runtime environment and application into the final Python image.
- `backend/docker-entrypoint.sh` applies committed Alembic migrations before Uvicorn starts.
- `frontend/Dockerfile` runs `npm ci` and the TypeScript/Vite production build in Node, then copies only `dist/` into an unprivileged Nginx image.
- `frontend/nginx.conf` serves the single-page application, caches fingerprinted assets, adds basic security headers, and proxies backend routes.
- `compose.yaml` defines health-aware startup order, the private network, published localhost ports, restart behavior, and persistent storage.
- Both `.dockerignore` files prevent local environments, dependencies, test output, and secrets from entering build contexts.

The Node and Python toolchains exist only in builder stages. They are not copied into the frontend runtime image, which reduces size and attack surface.

## Start the stack

Create the ignored Compose environment file once:

```bash
cp .env.example .env
```

Replace both occurrences of `CHANGE_ME_LOCAL_ONLY` with the same URL-safe password. Then build and start the stack:

```bash
docker compose up --build --detach --wait
```

`--detach` runs containers in the background. `--wait` returns only when all three health checks report healthy.

Useful endpoints:

- Dashboard and same-origin API proxy: `http://localhost:5173`
- Direct backend API: `http://localhost:8000`
- OpenAPI documentation through Nginx: `http://localhost:5173/docs`
- Database-aware readiness through Nginx: `http://localhost:5173/ready`

## Understand startup order

Compose waits for PostgreSQL's `pg_isready` check before starting FastAPI. The backend entrypoint runs `alembic upgrade head`, then starts Uvicorn. Nginx starts only after the backend's `/ready` endpoint confirms that both the API and database are available.

This is stronger than simple process ordering. A running database process may still be initializing, and a running API process may not be able to query its database. Health-based dependencies test usable service state.

## Inspect and troubleshoot

```bash
docker compose ps
docker compose logs --follow
docker compose logs --follow backend
docker compose exec backend id
docker compose exec frontend id
```

The `id` commands demonstrate that FastAPI runs as UID `10001` and Nginx runs as its unprivileged `nginx` user. Neither application container needs root at runtime.

Rebuild only one application after a code change:

```bash
docker compose build backend
docker compose up --detach --wait backend
```

Use `frontend` instead of `backend` for the React/Nginx image.

## Persistence and shutdown

Stop and remove containers and the private network while keeping database data:

```bash
docker compose down
```

The named `postgres-data` volume survives, so releases return the next time the stack starts.

To intentionally delete all Compose database data and begin from an empty database:

```bash
docker compose down --volumes
```

The second command is destructive. Use it only when losing local ReleaseGuard records is acceptable.

## Configuration and secrets

The root `.env` is ignored by Git. `.env.example` documents variable names using a placeholder, while the real password and database URL remain local. Later Kubernetes environments will inject equivalent values through Secrets rather than copying this file into an image.

Optional `FRONTEND_PORT` and `BACKEND_PORT` values change the host bindings if ports 5173 or 8000 are already used. Container ports and service-to-service names remain unchanged.
