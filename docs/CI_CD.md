# CI/CD and container security

ReleaseGuard uses a single GitHub Actions workflow at
`.github/workflows/ci-cd.yml`. It runs automatically for every push to `main`,
for pull requests targeting `main`, and manually through `workflow_dispatch`.

## Why the pipeline is ordered

The workflow is a sequence of gates:

1. **Backend tests** start an isolated PostgreSQL 17 service, install the
   locked Python dependencies, check dependency consistency, apply and verify
   Alembic migrations, and run all pytest tests with the 90% coverage gate.
2. **Frontend checks** install the exact npm lockfile, run ESLint, and create
   the production Vite bundle.
3. **Container delivery** starts only after both quality jobs pass. A matrix
   builds the backend and frontend images independently.
4. **Trivy security gate** inspects the operating-system and application
   packages in each built image. The job fails when a fixable `HIGH` or
   `CRITICAL` vulnerability is found.
5. **GHCR publication** happens only on `main` and only after the image passes
   Trivy. Pull requests build and scan images but never publish them.

This order matters: an image cannot be published when tests, linting, the
frontend build, or its security scan fails.

## Image identity

The published images are:

- `ghcr.io/nipun172006/releaseguard-backend:<git-sha>`
- `ghcr.io/nipun172006/releaseguard-frontend:<git-sha>`

The full Git commit SHA is immutable and connects a running container back to
the exact source revision and workflow run that produced it. ReleaseGuard does
not publish a mutable `latest` tag. Later, Helm and ArgoCD will receive this SHA
tag so Git remains the deployment source of truth.

## Permissions and secrets

The workflow defaults to read-only repository access. Only the container job
receives `packages: write`, which is the minimum permission needed to publish
to GHCR. Authentication uses GitHub's short-lived `GITHUB_TOKEN`; no personal
access token, registry password, or application secret is stored in the
repository.

## Trivy result meaning

Trivy scans the installed OS packages and language dependencies inside both
runtime images. `ignore-unfixed: true` keeps the gate actionable by blocking
only findings that currently have an upstream fix. During pipeline development,
Trivy found 65 HIGH and 3 CRITICAL fixable CVEs in the older Nginx 1.28 Alpine
runtime, including vulnerabilities in Nginx and OpenSSL. Updating the runtime
to the patched Nginx 1.30.6 / Alpine 3.24 image cleared the gate. A successful
scan means no fixable HIGH or CRITICAL CVE was detected in the package
databases available to that workflow run; it does not prove the image is free
from every possible security issue.

## Reading a run

Open the repository's **Actions** tab and choose the **CI/CD** workflow. The
dependency graph makes the gate visible: the two quality jobs must be green
before both container jobs run. Each container log contains the image build,
the Trivy table, and the final GHCR push with the exact SHA tag.

Verified example: [successful CI/CD run for commit `fcd9491`](https://github.com/nipun172006/releaseguard/actions/runs/38966071778). The corresponding frontend and backend Trivy summaries are saved in [`demo/evidence/trivy-scan.png`](../demo/evidence/trivy-scan.png).

For local checks before pushing:

```bash
cd backend
RELEASEGUARD_TEST_DATABASE_URL=postgresql+psycopg://releaseguard:releaseguard@localhost:5432/releaseguard_test .venv/bin/python -m pytest

cd ../frontend
npm run lint
npm run build

cd ..
docker build --check backend
docker build --check frontend
```

Dependabot checks the Python, npm, Docker, and GitHub Actions dependencies each
week so the pinned versions do not silently become stale.
