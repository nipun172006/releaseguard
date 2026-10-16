import {
  useDeferredValue,
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  ApiError,
  createRelease,
  deleteRelease,
  getApiBaseUrl,
  getHealth,
  getReleases,
  getStats,
  updateRelease,
} from './api'
import ReleaseDrawer from './components/ReleaseDrawer'
import ReleaseForm from './components/ReleaseForm'
import type {
  ReleaseFilters,
  ReleasePayload,
  ReleaseRecord,
  ReleaseStats,
  ReleaseUpdate,
} from './types'

type ApiState = 'checking' | 'healthy' | 'unavailable'
type Notice = { tone: 'success' | 'error'; message: string }

const emptyStats: ReleaseStats = {
  total_releases: 0,
  ready_to_deploy: 0,
  active_deployments: 0,
  high_or_critical_risk: 0,
  successful_deployments: 0,
  average_readiness_score: 0,
}

const emptyFilters: ReleaseFilters = {
  search: '',
  environment: '',
  status: '',
  risk: '',
}

function formatUpdatedAt(value: string): string {
  const date = new Date(value)
  const elapsed = Date.now() - date.getTime()
  const minutes = Math.floor(elapsed / 60_000)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`

  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`

  return new Intl.DateTimeFormat('en', {
    day: '2-digit',
    month: 'short',
    year: date.getFullYear() === new Date().getFullYear() ? undefined : 'numeric',
  }).format(date)
}

function readableError(error: unknown): string {
  if (error instanceof ApiError) return error.message
  if (error instanceof Error) return error.message
  return 'Something unexpected happened. Please try again.'
}

function App() {
  const [apiState, setApiState] = useState<ApiState>('checking')
  const [releases, setReleases] = useState<ReleaseRecord[]>([])
  const [stats, setStats] = useState<ReleaseStats>(emptyStats)
  const [filters, setFilters] = useState<ReleaseFilters>(emptyFilters)
  const deferredFilters = useDeferredValue(filters)
  const [isLoading, setIsLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)
  const [selectedRelease, setSelectedRelease] = useState<ReleaseRecord | null>(null)
  const [formRelease, setFormRelease] = useState<ReleaseRecord | 'new' | null>(null)
  const [formError, setFormError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [isMutating, setIsMutating] = useState(false)
  const [notice, setNotice] = useState<Notice | null>(null)

  const activeFilterCount = useMemo(
    () => Object.values(filters).filter(Boolean).length,
    [filters],
  )

  useEffect(() => {
    const controller = new AbortController()

    getHealth(controller.signal)
      .then(() => setApiState('healthy'))
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === 'AbortError') return
        setApiState('unavailable')
      })

    return () => controller.abort()
  }, [refreshKey])

  useEffect(() => {
    const controller = new AbortController()

    Promise.all([
      getReleases(deferredFilters, controller.signal),
      getStats(controller.signal),
    ])
      .then(([releaseData, statsData]) => {
        setReleases(releaseData)
        setStats(statsData)
        setSelectedRelease((current) => {
          if (!current) return null
          return releaseData.find((release) => release.id === current.id) ?? current
        })
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === 'AbortError') return
        setLoadError(readableError(error))
      })
      .finally(() => {
        if (!controller.signal.aborted) setIsLoading(false)
      })

    return () => controller.abort()
  }, [deferredFilters, refreshKey])

  useEffect(() => {
    if (!notice) return
    const timer = window.setTimeout(() => setNotice(null), 4500)
    return () => window.clearTimeout(timer)
  }, [notice])

  function refreshDashboard() {
    setIsLoading(true)
    setLoadError(null)
    setRefreshKey((current) => current + 1)
  }

  function updateFilter<Key extends keyof ReleaseFilters>(
    key: Key,
    value: ReleaseFilters[Key],
  ) {
    setIsLoading(true)
    setLoadError(null)
    setFilters((current) => ({ ...current, [key]: value }))
  }

  function clearAllFilters() {
    setIsLoading(true)
    setLoadError(null)
    setFilters(emptyFilters)
  }

  function openCreateForm() {
    setFormError(null)
    setFormRelease('new')
  }

  function openEditForm() {
    if (!selectedRelease) return
    setFormError(null)
    setFormRelease(selectedRelease)
  }

  async function submitRelease(payload: ReleasePayload) {
    setIsSaving(true)
    setFormError(null)

    try {
      const saved =
        formRelease === 'new'
          ? await createRelease(payload)
          : await updateRelease(formRelease!.id, payload)

      setSelectedRelease(saved)
      setFormRelease(null)
      setNotice({
        tone: 'success',
        message: formRelease === 'new' ? 'Release created.' : 'Release updated.',
      })
      refreshDashboard()
    } catch (error) {
      setFormError(readableError(error))
    } finally {
      setIsSaving(false)
    }
  }

  async function updateSelectedRelease(payload: ReleaseUpdate) {
    if (!selectedRelease) return
    setIsMutating(true)

    try {
      const updated = await updateRelease(selectedRelease.id, payload)
      setSelectedRelease(updated)
      setNotice({ tone: 'success', message: 'Release updated.' })
      refreshDashboard()
    } catch (error) {
      setNotice({ tone: 'error', message: readableError(error) })
    } finally {
      setIsMutating(false)
    }
  }

  async function removeSelectedRelease() {
    if (!selectedRelease) return

    const confirmed = window.confirm(
      `Delete ${selectedRelease.application_name} v${selectedRelease.version}? This cannot be undone.`,
    )
    if (!confirmed) return

    setIsMutating(true)
    try {
      await deleteRelease(selectedRelease.id)
      setSelectedRelease(null)
      setNotice({ tone: 'success', message: 'Draft release deleted.' })
      refreshDashboard()
    } catch (error) {
      setNotice({ tone: 'error', message: readableError(error) })
    } finally {
      setIsMutating(false)
    }
  }

  return (
    <div className="application-layout">
      <aside className="sidebar">
        <a className="brand" href="#dashboard" aria-label="ReleaseGuard dashboard">
          <span className="brand-mark">RG</span>
          <span>
            <strong>ReleaseGuard</strong>
            <small>Control center</small>
          </span>
        </a>

        <nav className="sidebar-nav" aria-label="Primary navigation">
          <a className="nav-item nav-item--active" href="#dashboard">
            <span className="nav-symbol">⌂</span>
            Overview
          </a>
          <a className="nav-item" href="#releases">
            <span className="nav-symbol">↗</span>
            Releases
            <span className="nav-count">{stats.total_releases}</span>
          </a>
          <a className="nav-item" href="#readiness">
            <span className="nav-symbol">✓</span>
            Readiness
          </a>
        </nav>

        <div className="sidebar-section">
          <span className="sidebar-label">Workspace</span>
          <div className="workspace-card">
            <span className={`api-indicator api-indicator--${apiState}`} />
            <div>
              <strong>Local environment</strong>
              <small>
                {apiState === 'healthy'
                  ? 'API connected'
                  : apiState === 'checking'
                    ? 'Checking API…'
                    : 'API unavailable'}
              </small>
            </div>
          </div>
        </div>

        <div className="sidebar-footer">
          <a href={`${getApiBaseUrl()}/docs`} target="_blank" rel="noreferrer">
            API documentation <span>↗</span>
          </a>
          <span>ReleaseGuard · DevSecOps capstone</span>
        </div>
      </aside>

      <main className="workspace" id="dashboard">
        <header className="workspace-header">
          <div>
            <span className="page-eyebrow">Deployment operations</span>
            <h1>Release overview</h1>
            <p>One view of readiness evidence, deployment risk, and release outcomes.</p>
          </div>
          <div className="header-actions">
            <button
              className="refresh-button"
              type="button"
              onClick={refreshDashboard}
              disabled={isLoading}
              aria-label="Refresh dashboard"
            >
              ↻
            </button>
            <button className="button button--primary button--new" type="button" onClick={openCreateForm}>
              <span>+</span> New release
            </button>
          </div>
        </header>

        {apiState === 'unavailable' && (
          <div className="connection-banner" role="alert">
            <span>!</span>
            <div>
              <strong>The ReleaseGuard API is unavailable.</strong>
              <p>Start the backend on port 8000, then refresh this dashboard.</p>
            </div>
            <button type="button" onClick={refreshDashboard}>Retry</button>
          </div>
        )}

        <section className="stats-grid" id="readiness" aria-label="Release statistics">
          <article className="stat-card stat-card--accent">
            <div className="stat-topline"><span>Total releases</span><i>01</i></div>
            <strong>{stats.total_releases}</strong>
            <p>All tracked release candidates</p>
          </article>
          <article className="stat-card">
            <div className="stat-topline"><span>Ready to deploy</span><i className="dot dot--green" /></div>
            <strong>{stats.ready_to_deploy}</strong>
            <p>Mandatory evidence complete</p>
          </article>
          <article className="stat-card">
            <div className="stat-topline"><span>Deploying now</span><i className="dot dot--blue" /></div>
            <strong>{stats.active_deployments}</strong>
            <p>Active rollout operations</p>
          </article>
          <article className="stat-card">
            <div className="stat-topline"><span>At risk</span><i className="dot dot--red" /></div>
            <strong>{stats.high_or_critical_risk}</strong>
            <p>High or critical attention</p>
          </article>
          <article className="stat-card">
            <div className="stat-topline"><span>Successful</span><i className="dot dot--green" /></div>
            <strong>{stats.successful_deployments}</strong>
            <p>Completed deployments</p>
          </article>
          <article className="stat-card">
            <div className="stat-topline"><span>Average readiness</span><i>AVG</i></div>
            <strong>{Math.round(stats.average_readiness_score)}<small>%</small></strong>
            <p>Across the complete portfolio</p>
          </article>
        </section>

        <section className="release-section" id="releases" aria-labelledby="release-section-title">
          <div className="release-section-header">
            <div>
              <span className="section-kicker">Release portfolio</span>
              <h2 id="release-section-title">Deployment queue</h2>
              <p>Open a release to review evidence or move it through the lifecycle.</p>
            </div>
            <div className="result-count">
              <strong>{releases.length}</strong>
              <span>{releases.length === 1 ? 'result' : 'results'}</span>
            </div>
          </div>

          <div className="filter-bar">
            <label className="search-field">
              <span aria-hidden="true">⌕</span>
              <input
                value={filters.search}
                onChange={(event) => updateFilter('search', event.target.value)}
                placeholder="Search application or version"
                aria-label="Search releases"
              />
            </label>

            <label className="filter-field">
              <span>Environment</span>
              <select
                aria-label="Filter by environment"
                value={filters.environment}
                onChange={(event) =>
                  updateFilter('environment', event.target.value as ReleaseFilters['environment'])
                }
              >
                <option value="">All</option>
                <option value="DEVELOPMENT">Development</option>
                <option value="STAGING">Staging</option>
                <option value="PRODUCTION">Production</option>
              </select>
            </label>

            <label className="filter-field">
              <span>Status</span>
              <select
                aria-label="Filter by status"
                value={filters.status}
                onChange={(event) =>
                  updateFilter('status', event.target.value as ReleaseFilters['status'])
                }
              >
                <option value="">All</option>
                <option value="DRAFT">Draft</option>
                <option value="READY">Ready</option>
                <option value="DEPLOYING">Deploying</option>
                <option value="SUCCESS">Success</option>
                <option value="FAILED">Failed</option>
                <option value="ROLLED_BACK">Rolled back</option>
              </select>
            </label>

            <label className="filter-field">
              <span>Risk</span>
              <select
                aria-label="Filter by risk"
                value={filters.risk}
                onChange={(event) =>
                  updateFilter('risk', event.target.value as ReleaseFilters['risk'])
                }
              >
                <option value="">All</option>
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </label>

            {activeFilterCount > 0 && (
              <button className="clear-filters" type="button" onClick={clearAllFilters}>
                Clear {activeFilterCount}
              </button>
            )}
          </div>

          <div className="table-shell">
            {loadError ? (
              <div className="state-panel state-panel--error">
                <span>!</span>
                <h3>We couldn’t load the release queue</h3>
                <p>{loadError}</p>
                <button className="button button--secondary" type="button" onClick={refreshDashboard}>
                  Try again
                </button>
              </div>
            ) : isLoading ? (
              <div className="loading-table" aria-label="Loading releases">
                {Array.from({ length: 4 }, (_, index) => (
                  <div className="skeleton-row" key={index}>
                    <span /><span /><span /><span /><span />
                  </div>
                ))}
              </div>
            ) : releases.length === 0 ? (
              <div className="state-panel">
                <span className="empty-mark">RG</span>
                <h3>{activeFilterCount ? 'No releases match these filters' : 'Your release queue is empty'}</h3>
                <p>
                  {activeFilterCount
                    ? 'Clear or adjust the filters to widen the result set.'
                    : 'Create the first release candidate to begin collecting readiness evidence.'}
                </p>
                <button
                  className="button button--primary"
                  type="button"
                  onClick={activeFilterCount ? clearAllFilters : openCreateForm}
                >
                  {activeFilterCount ? 'Clear filters' : 'Create first release'}
                </button>
              </div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Release</th>
                    <th>Environment</th>
                    <th>Status</th>
                    <th>Readiness</th>
                    <th>Risk</th>
                    <th>Owner</th>
                    <th>Updated</th>
                    <th aria-label="Actions" />
                  </tr>
                </thead>
                <tbody>
                  {releases.map((release) => (
                    <tr key={release.id} onClick={() => setSelectedRelease(release)}>
                      <td data-label="Release">
                        <div className="release-cell">
                          <span>{release.application_name.slice(0, 2).toUpperCase()}</span>
                          <div>
                            <strong>{release.application_name}</strong>
                            <small>v{release.version}</small>
                          </div>
                        </div>
                      </td>
                      <td data-label="Environment">
                        <span className="environment-pill">{release.environment}</span>
                      </td>
                      <td data-label="Status">
                        <span className={`badge badge--status-${release.status.toLowerCase()}`}>
                          {release.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td data-label="Readiness">
                        <div className="readiness-cell">
                          <div><span style={{ width: `${release.readiness_score}%` }} /></div>
                          <strong>{release.readiness_score}%</strong>
                        </div>
                      </td>
                      <td data-label="Risk">
                        <span className={`badge badge--risk-${release.risk_level.toLowerCase()}`}>
                          <i /> {release.risk_level}
                        </span>
                      </td>
                      <td data-label="Owner"><span className="owner-name">{release.owner}</span></td>
                      <td data-label="Updated"><span className="updated-at">{formatUpdatedAt(release.updated_at)}</span></td>
                      <td><button className="row-action" type="button" aria-label={`Open ${release.application_name}`}>›</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </section>

        <footer className="workspace-footer">
          <span>Ship only when the evidence says ready.</span>
          <span>API: {getApiBaseUrl() || 'same origin'}</span>
        </footer>
      </main>

      {selectedRelease && (
        <ReleaseDrawer
          release={selectedRelease}
          isBusy={isMutating}
          onClose={() => setSelectedRelease(null)}
          onEdit={openEditForm}
          onUpdate={updateSelectedRelease}
          onDelete={removeSelectedRelease}
        />
      )}

      {formRelease && (
        <ReleaseForm
          key={formRelease === 'new' ? 'new' : formRelease.id}
          release={formRelease === 'new' ? undefined : formRelease}
          isSaving={isSaving}
          error={formError}
          onClose={() => setFormRelease(null)}
          onSubmit={submitRelease}
        />
      )}

      {notice && (
        <div className={`toast toast--${notice.tone}`} role="status">
          <span>{notice.tone === 'success' ? '✓' : '!'}</span>
          {notice.message}
          <button type="button" onClick={() => setNotice(null)} aria-label="Dismiss notification">×</button>
        </div>
      )}
    </div>
  )
}

export default App
