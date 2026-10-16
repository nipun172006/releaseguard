import type {
  CheckField,
  ReleaseRecord,
  ReleaseStatus,
  ReleaseUpdate,
} from '../types'

type ReleaseDrawerProps = {
  release: ReleaseRecord
  isBusy: boolean
  onClose: () => void
  onEdit: () => void
  onUpdate: (payload: ReleaseUpdate) => Promise<void>
  onDelete: () => Promise<void>
}

const checks: Array<{
  field: CheckField
  label: string
  requiredEverywhere: boolean
}> = [
  { field: 'tests_passed', label: 'Automated tests', requiredEverywhere: true },
  { field: 'security_scan_passed', label: 'Security scan', requiredEverywhere: true },
  { field: 'approval_received', label: 'Deployment approval', requiredEverywhere: false },
  { field: 'backup_confirmed', label: 'Backup confirmation', requiredEverywhere: false },
  { field: 'rollback_plan_ready', label: 'Rollback plan', requiredEverywhere: true },
]

const transitions: Record<
  ReleaseStatus,
  Array<{ status: ReleaseStatus; label: string; tone: string }>
> = {
  DRAFT: [{ status: 'READY', label: 'Mark ready', tone: 'primary' }],
  READY: [
    { status: 'DEPLOYING', label: 'Start deployment', tone: 'primary' },
    { status: 'DRAFT', label: 'Return to draft', tone: 'secondary' },
  ],
  DEPLOYING: [
    { status: 'SUCCESS', label: 'Mark successful', tone: 'success' },
    { status: 'FAILED', label: 'Mark failed', tone: 'danger' },
  ],
  FAILED: [
    { status: 'DEPLOYING', label: 'Retry deployment', tone: 'primary' },
    { status: 'ROLLED_BACK', label: 'Confirm rollback', tone: 'danger' },
  ],
  SUCCESS: [{ status: 'ROLLED_BACK', label: 'Record rollback', tone: 'danger' }],
  ROLLED_BACK: [],
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('en', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

export default function ReleaseDrawer({
  release,
  isBusy,
  onClose,
  onEdit,
  onUpdate,
  onDelete,
}: ReleaseDrawerProps) {
  const scoreColor =
    release.risk_level === 'LOW'
      ? '#18a679'
      : release.risk_level === 'MEDIUM'
        ? '#e1a528'
        : '#e85d54'

  return (
    <div className="drawer-backdrop" role="presentation" onMouseDown={onClose}>
      <aside
        className="release-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="release-detail-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="drawer-header">
          <button className="icon-button" type="button" onClick={onClose} aria-label="Close details">
            ×
          </button>
          <button className="text-button" type="button" onClick={onEdit}>
            Edit release
          </button>
        </header>

        <div className="drawer-content">
          <div className="detail-identity">
            <span className="environment-label">{release.environment}</span>
            <h2 id="release-detail-title">{release.application_name}</h2>
            <div className="release-version">v{release.version}</div>
            <div className="badge-row">
              <span className={`badge badge--status-${release.status.toLowerCase()}`}>
                {release.status.replace('_', ' ')}
              </span>
              <span className={`badge badge--risk-${release.risk_level.toLowerCase()}`}>
                {release.risk_level} RISK
              </span>
            </div>
          </div>

          <section className="readiness-panel">
            <div
              className="score-ring"
              style={{
                background: `conic-gradient(${scoreColor} ${release.readiness_score}%, #e8edf1 0)`,
              }}
              aria-label={`${release.readiness_score} percent ready`}
            >
              <div>
                <strong>{release.readiness_score}</strong>
                <span>/ 100</span>
              </div>
            </div>
            <div className="readiness-copy">
              <span className="section-kicker">Readiness score</span>
              <h3>{release.is_ready ? 'Evidence complete' : 'Action required'}</h3>
              <p>
                {release.is_ready
                  ? 'Every mandatory check for this environment is complete.'
                  : `${release.blockers.length} mandatory ${release.blockers.length === 1 ? 'check is' : 'checks are'} still missing.`}
              </p>
            </div>
          </section>

          {release.blockers.length > 0 && (
            <section className="blocker-panel" aria-labelledby="blockers-title">
              <div className="blocker-title">
                <span aria-hidden="true">!</span>
                <strong id="blockers-title">Deployment blockers</strong>
              </div>
              <ul>
                {release.blockers.map((blocker) => <li key={blocker}>{blocker}</li>)}
              </ul>
            </section>
          )}

          <section className="detail-section">
            <div className="detail-section-heading">
              <div>
                <span className="section-kicker">Evidence</span>
                <h3>Readiness checklist</h3>
              </div>
              <span className="save-hint">Changes save instantly</span>
            </div>

            <div className="detail-check-list">
              {checks.map((check) => {
                const required =
                  check.requiredEverywhere || release.environment === 'PRODUCTION'
                const complete = release[check.field]

                return (
                  <button
                    className={`detail-check ${complete ? 'detail-check--complete' : ''}`}
                    type="button"
                    role="switch"
                    aria-checked={complete}
                    disabled={isBusy}
                    key={check.field}
                    onClick={() => onUpdate({ [check.field]: !complete })}
                  >
                    <span className="detail-check-mark">{complete ? '✓' : ''}</span>
                    <span>
                      <strong>{check.label}</strong>
                      <small>{required ? 'Mandatory' : 'Recommended'}</small>
                    </span>
                    <span className={`requirement-tag ${required ? 'requirement-tag--required' : ''}`}>
                      {required ? 'Required' : 'Optional'}
                    </span>
                  </button>
                )
              })}
            </div>
          </section>

          <section className="detail-section detail-section--metadata">
            <span className="section-kicker">Context</span>
            <h3>Release information</h3>
            <dl className="metadata-grid">
              <div>
                <dt>Owner</dt>
                <dd>{release.owner}</dd>
              </div>
              <div>
                <dt>Last updated</dt>
                <dd>{formatDate(release.updated_at)}</dd>
              </div>
              <div className="metadata-wide">
                <dt>Description</dt>
                <dd>{release.description || 'No description provided.'}</dd>
              </div>
              <div className="metadata-wide">
                <dt>Deployment notes</dt>
                <dd>{release.deployment_notes || 'No deployment notes yet.'}</dd>
              </div>
            </dl>
          </section>
        </div>

        <footer className="drawer-footer">
          {transitions[release.status].length > 0 ? (
            <div className="lifecycle-actions">
              {transitions[release.status].map((action) => {
                const readinessBlocked =
                  action.status === 'READY' && !release.is_ready

                return (
                  <button
                    className={`button button--${action.tone}`}
                    type="button"
                    disabled={isBusy || readinessBlocked}
                    title={readinessBlocked ? 'Complete mandatory checks first' : undefined}
                    key={action.status}
                    onClick={() => onUpdate({ status: action.status })}
                  >
                    {action.label}
                  </button>
                )
              })}
            </div>
          ) : (
            <p className="terminal-state">This release has reached its final lifecycle state.</p>
          )}

          {release.status === 'DRAFT' && (
            <button
              className="delete-button"
              type="button"
              disabled={isBusy}
              onClick={onDelete}
            >
              Delete draft
            </button>
          )}
        </footer>
      </aside>
    </div>
  )
}
