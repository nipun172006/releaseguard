# ReleaseGuard Product Specification

## 1. Product identity

| Field | Decision |
| --- | --- |
| Name | ReleaseGuard |
| Tagline | Ship only when the evidence says ready. |
| Product type | Deployment readiness and release-risk control center |
| Primary audience | Developers, DevOps engineers, release managers, and engineering leads |
| Core value | Replace informal release decisions with a visible, repeatable readiness process |

## 2. Problem statement

Teams often decide whether to deploy through chat messages, memory, and disconnected tools. A release can be approved even when tests have failed, a security scan is missing, or no rollback plan exists. This creates avoidable production risk and makes it difficult to explain why a deployment was considered safe.

ReleaseGuard provides one place to:

- Register an upcoming release.
- Record the evidence required before deployment.
- Calculate readiness using explicit rules.
- Surface missing checks and high-risk conditions.
- Track the release outcome and rollback state.
- Give the team a shared view of deployment health.

ReleaseGuard does not execute deployments. It is the decision and visibility layer around the deployment process.

## 3. Product goals

1. Make release readiness visible and explainable.
2. Prevent a release from being marked ready when mandatory checks are missing.
3. Provide useful dashboard statistics for release activity and risk.
4. Demonstrate real backend business logic rather than only basic CRUD storage.
5. Remain small enough to deploy, operate, monitor, and explain end to end.

## 4. Non-goals for the initial version

The first version will not include:

- User authentication or organization-level authorization.
- Direct deployment to external customer systems.
- Live integrations with Jira, Jenkins, GitHub, or cloud providers.
- Machine-learning risk prediction.
- Email, Slack, or SMS notifications.
- Multi-tenant billing or subscription management.

These are valid future improvements, but they are outside the current release.

## 5. Primary user journey

```text
Create release
    |
    v
Enter application, version, environment, owner, and notes
    |
    v
Complete readiness checks
    |
    v
ReleaseGuard calculates score, risk, and blockers
    |
    +---- blockers remain ----> keep release in DRAFT
    |
    `---- mandatory checks pass ----> mark READY
                                      |
                                      v
                                  DEPLOYING
                                      |
                         +------------+------------+
                         |                         |
                         v                         v
                      SUCCESS                   FAILED
                                                    |
                                                    v
                                              ROLLED_BACK
```

## 6. Release lifecycle

Allowed statuses:

```text
DRAFT
READY
DEPLOYING
SUCCESS
FAILED
ROLLED_BACK
```

Allowed transitions:

| Current status | Allowed next statuses | Rule |
| --- | --- | --- |
| DRAFT | READY | All mandatory readiness checks must pass |
| READY | DRAFT, DEPLOYING | A check becoming incomplete returns the release to DRAFT |
| DEPLOYING | SUCCESS, FAILED | Deployment outcome must be recorded |
| FAILED | ROLLED_BACK, DEPLOYING | A retry or rollback is allowed |
| SUCCESS | ROLLED_BACK | Used when a successful release later requires rollback |
| ROLLED_BACK | No transition in MVP | Create a new release for another attempt |

Invalid transitions will return an HTTP `409 Conflict` response with an explanatory message.

## 7. Readiness checks

Each release tracks five explicit checks:

| Check | Mandatory | Weight | Meaning |
| --- | --- | ---: | --- |
| Automated tests passed | Yes | 25 | The application passed its automated test suite |
| Security scan passed | Yes | 25 | The release artifact passed the required vulnerability gate |
| Deployment approval received | Yes for production | 20 | An authorized reviewer approved the release |
| Backup confirmed | Yes for production | 15 | Required state can be recovered if deployment fails |
| Rollback plan ready | Yes | 15 | The team knows how to return to the previous version |

The score is deterministic and explainable:

```text
readiness_score = sum of weights for completed checks
```

Approval and backup are optional for development, recommended for staging, and mandatory for production. Tests, security scanning, and a rollback plan are mandatory in every environment.

## 8. Risk calculation

Risk is calculated from readiness evidence and deployment context.

### Critical risk

Any of the following:

- Production release with failed or missing automated tests.
- Production release with failed or missing security scan.
- Production release without a rollback plan.
- A failed deployment that has not been rolled back.

### High risk

Any of the following when no critical condition exists:

- Production approval is missing.
- Production backup confirmation is missing.
- Readiness score is below 70.

### Medium risk

- Readiness score is between 70 and 99.
- A staging release is missing a recommended approval or backup check.

### Low risk

- Readiness score is 100.
- All checks required for the selected environment pass.
- No unresolved deployment failure exists.

The API will return both the risk level and human-readable blockers so the result is never a mysterious number.

## 9. Data model

### Release

| Field | Type | Rules |
| --- | --- | --- |
| `id` | Integer | Primary key |
| `application_name` | String(120) | Required |
| `version` | String(50) | Required |
| `environment` | Enum-like string | `DEVELOPMENT`, `STAGING`, or `PRODUCTION` |
| `owner` | String(120) | Required |
| `description` | Text | Optional |
| `status` | Enum-like string | Defaults to `DRAFT` |
| `tests_passed` | Boolean | Defaults to false |
| `security_scan_passed` | Boolean | Defaults to false |
| `approval_received` | Boolean | Defaults to false |
| `backup_confirmed` | Boolean | Defaults to false |
| `rollback_plan_ready` | Boolean | Defaults to false |
| `deployment_notes` | Text | Optional |
| `created_at` | Timestamp with timezone | Set by backend |
| `updated_at` | Timestamp with timezone | Updated by backend |

The following values are calculated rather than stored:

- `readiness_score`
- `risk_level`
- `blockers`

Keeping calculated values out of the database prevents stale results when readiness checks change.

### Database constraints

- Application name and version cannot be empty.
- Version is unique per application and environment.
- Status and environment values are validated by the API.
- Timestamps are stored in UTC.

## 10. REST API contract

### Platform endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Service metadata and documentation link |
| GET | `/health` | Lightweight process liveness |
| GET | `/ready` | Database-aware readiness |
| GET | `/metrics` | Prometheus-formatted application metrics |

### Release endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/releases` | List releases with optional status, environment, and risk filters |
| GET | `/api/releases/{id}` | Retrieve one release |
| POST | `/api/releases` | Create a release |
| PUT | `/api/releases/{id}` | Update metadata, checks, or lifecycle status |
| DELETE | `/api/releases/{id}` | Delete a draft release |
| GET | `/api/releases/stats` | Dashboard counts and readiness summary |
| GET | `/api/releases/{id}/readiness` | Score, risk, mandatory checks, and blockers |

### Important API behaviour

- Creating a release returns `201 Created`.
- Deleting successfully returns `204 No Content`.
- Missing releases return `404 Not Found`.
- Invalid lifecycle transitions return `409 Conflict`.
- Validation failures return `422 Unprocessable Entity`.
- Only `DRAFT` releases can be deleted.
- List filters are implemented on the server rather than only in the browser.

## 11. Dashboard requirements

The dashboard will show:

- Total releases.
- Releases ready to deploy.
- Active deployments.
- High or critical-risk releases.
- Successful deployments.
- Average readiness score.

The release table will support:

- Search by application name or version.
- Filter by environment.
- Filter by status.
- Filter by risk.
- Clear visual badges for status and risk.
- Direct access to release details.

## 12. Release detail requirements

The detail view will include:

- Release identity and owner.
- Current lifecycle status.
- Readiness progress indicator.
- Risk explanation.
- Checklist with mandatory and recommended labels.
- Blockers that must be addressed.
- Deployment notes.
- Allowed status actions.

The interface must disable or clearly reject actions that violate lifecycle rules.

## 13. Visual direction

ReleaseGuard should feel like a professional internal engineering tool:

- Dark navigation sidebar.
- Light dashboard workspace.
- Deep navy base colors.
- Green for successful and low-risk states.
- Amber for warnings and medium risk.
- Red for failure and critical risk.
- Strong information hierarchy with restrained animation.
- Responsive behaviour for laptop, tablet, and mobile widths.

## 14. Non-functional requirements

### Reliability

- Liveness and readiness endpoints have different responsibilities.
- Database sessions are always closed.
- Kubernetes readiness prevents traffic from reaching an unavailable backend.
- Containers stop cleanly and report failures through exit status.

### Security

- Containers run as non-root users.
- No real credentials are committed.
- Input is validated using Pydantic schemas.
- CI scans both images with Trivy.
- Images use immutable Git SHA tags.
- Runtime configuration is supplied externally.

### Testability

- Business rules are kept in testable functions or services.
- Tests use an isolated database.
- At least nine API tests cover success and failure paths.

### Observability

- FastAPI exposes Prometheus metrics.
- Logs are written to standard output.
- Grafana visualizes total requests, request rate, and average request duration.

### Portability

- The complete local stack starts with Docker Compose.
- The same application images run in Kubernetes.
- Environment-specific values are outside the image.

## 15. Definition of done for the application layer

The application itself is complete when:

```text
[x] Alembic creates the releases table from an empty database
[x] FastAPI exposes every documented endpoint
[x] Readiness and risk calculations match this specification
[x] Invalid lifecycle transitions are rejected
[x] At least nine automated tests pass
[x] React provides complete create, read, update, and delete workflows
[x] Filters and dashboard statistics work
[x] The interface is responsive and has loading, empty, and error states
[x] /health, /ready, and /metrics return valid responses
```

## 16. Example workflow

One complete release workflow is:

1. Create release `payments-api` version `2.4.0` for production.
2. Leave the security scan and rollback plan incomplete.
3. Observe the critical-risk result and deployment blockers.
4. Attempt to mark the release ready and confirm that the API rejects it.
5. Complete every mandatory check.
6. Confirm that readiness becomes 100% and risk becomes low.
7. Move the release through `READY`, `DEPLOYING`, and `SUCCESS`.
8. Generate traffic and observe application metrics in Grafana.
