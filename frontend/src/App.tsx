import { useEffect, useState } from 'react'

type ApiState = 'checking' | 'healthy' | 'unavailable'

type HealthResponse = {
  status: 'healthy'
  service: string
  environment: string
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

function App() {
  const [apiState, setApiState] = useState<ApiState>('checking')
  const [health, setHealth] = useState<HealthResponse | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    async function checkApi() {
      try {
        const response = await fetch(`${apiBaseUrl}/health`, {
          signal: controller.signal,
        })

        if (!response.ok) {
          throw new Error(`Health check returned ${response.status}`)
        }

        const result = (await response.json()) as HealthResponse
        setHealth(result)
        setApiState('healthy')
      } catch (error) {
        if (error instanceof DOMException && error.name === 'AbortError') {
          return
        }

        setApiState('unavailable')
      }
    }

    void checkApi()

    return () => controller.abort()
  }, [])

  return (
    <main className="app-shell">
      <nav className="topbar" aria-label="Primary navigation">
        <a className="brand" href="/" aria-label="ReleaseGuard home">
          <span className="brand-mark">RG</span>
          <span>ReleaseGuard</span>
        </a>
        <span className="phase-label">Foundation · Step 4</span>
      </nav>

      <section className="hero">
        <div className="eyebrow">Deployment readiness control center</div>
        <h1>
          Ship only when the
          <span> evidence says ready.</span>
        </h1>
        <p className="hero-copy">
          ReleaseGuard will turn test results, security checks, approvals,
          backups, and rollback plans into a clear release decision.
        </p>
      </section>

      <section className="status-grid" aria-label="Bootstrap status">
        <article className="status-card status-card--primary">
          <div className="card-heading">
            <span>API connection</span>
            <span className={`status-dot status-dot--${apiState}`} />
          </div>
          <strong>{apiState === 'healthy' ? 'Connected' : apiState}</strong>
          <p>
            {health
              ? `${health.service} is healthy in ${health.environment}.`
              : `Checking ${apiBaseUrl}/health`}
          </p>
        </article>

        <article className="status-card">
          <div className="card-heading">
            <span>Current milestone</span>
            <span className="step-number">04</span>
          </div>
          <strong>Release intelligence</strong>
          <p>PostgreSQL, CRUD, scoring, blockers, and lifecycle guardrails.</p>
        </article>

        <article className="status-card">
          <div className="card-heading">
            <span>Next milestone</span>
            <span className="step-number">05</span>
          </div>
          <strong>Automated tests</strong>
          <p>Turn every success and failure path into repeatable evidence.</p>
        </article>
      </section>
    </main>
  )
}

export default App
