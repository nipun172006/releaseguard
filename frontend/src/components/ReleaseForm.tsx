import { useState, type FormEvent } from 'react'

import type {
  CheckField,
  ReleaseEnvironment,
  ReleasePayload,
  ReleaseRecord,
} from '../types'

type ReleaseFormProps = {
  release?: ReleaseRecord
  isSaving: boolean
  error: string | null
  onClose: () => void
  onSubmit: (payload: ReleasePayload) => Promise<void>
}

type FormState = Omit<ReleasePayload, 'description' | 'deployment_notes'> & {
  description: string
  deployment_notes: string
}

const checks: Array<{
  field: CheckField
  label: string
  detail: string
  weight: number
}> = [
  {
    field: 'tests_passed',
    label: 'Automated tests passed',
    detail: 'Required in every environment',
    weight: 25,
  },
  {
    field: 'security_scan_passed',
    label: 'Security scan passed',
    detail: 'Required in every environment',
    weight: 25,
  },
  {
    field: 'approval_received',
    label: 'Deployment approval received',
    detail: 'Required for production',
    weight: 20,
  },
  {
    field: 'backup_confirmed',
    label: 'Backup confirmed',
    detail: 'Required for production',
    weight: 15,
  },
  {
    field: 'rollback_plan_ready',
    label: 'Rollback plan ready',
    detail: 'Required in every environment',
    weight: 15,
  },
]

function initialState(release?: ReleaseRecord): FormState {
  return {
    application_name: release?.application_name ?? '',
    version: release?.version ?? '',
    environment: release?.environment ?? 'STAGING',
    owner: release?.owner ?? '',
    description: release?.description ?? '',
    tests_passed: release?.tests_passed ?? false,
    security_scan_passed: release?.security_scan_passed ?? false,
    approval_received: release?.approval_received ?? false,
    backup_confirmed: release?.backup_confirmed ?? false,
    rollback_plan_ready: release?.rollback_plan_ready ?? false,
    deployment_notes: release?.deployment_notes ?? '',
  }
}

export default function ReleaseForm({
  release,
  isSaving,
  error,
  onClose,
  onSubmit,
}: ReleaseFormProps) {
  const [form, setForm] = useState<FormState>(() => initialState(release))

  const score = checks.reduce(
    (total, check) => total + (form[check.field] ? check.weight : 0),
    0,
  )

  function updateText(
    field: 'application_name' | 'version' | 'owner' | 'description' | 'deployment_notes',
    value: string,
  ) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  function updateEnvironment(value: ReleaseEnvironment) {
    setForm((current) => ({ ...current, environment: value }))
  }

  function updateCheck(field: CheckField, value: boolean) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    await onSubmit({
      ...form,
      application_name: form.application_name.trim(),
      version: form.version.trim(),
      owner: form.owner.trim(),
      description: form.description.trim() || null,
      deployment_notes: form.deployment_notes.trim() || null,
    })
  }

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        className="release-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="release-form-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="modal-header">
          <div>
            <span className="section-kicker">Release record</span>
            <h2 id="release-form-title">
              {release ? 'Edit release' : 'Create a new release'}
            </h2>
            <p>
              {release
                ? 'Update its metadata and the evidence used to calculate readiness.'
                : 'Register a candidate, then build the evidence required to deploy it.'}
            </p>
          </div>
          <button className="icon-button" type="button" onClick={onClose} aria-label="Close form">
            ×
          </button>
        </header>

        <form onSubmit={handleSubmit}>
          <div className="modal-content">
            {error && <div className="form-error" role="alert">{error}</div>}

            <div className="form-section-heading">
              <div>
                <span>01</span>
                <strong>Release identity</strong>
              </div>
              <p>What is being shipped, where, and by whom?</p>
            </div>

            <div className="form-grid">
              <label className="field field--wide">
                <span>Application name</span>
                <input
                  required
                  maxLength={120}
                  value={form.application_name}
                  onChange={(event) => updateText('application_name', event.target.value)}
                  placeholder="payments-api"
                />
              </label>

              <label className="field">
                <span>Version</span>
                <input
                  required
                  maxLength={50}
                  value={form.version}
                  onChange={(event) => updateText('version', event.target.value)}
                  placeholder="2.4.0"
                />
              </label>

              <label className="field">
                <span>Environment</span>
                <select
                  aria-label="Environment"
                  value={form.environment}
                  onChange={(event) =>
                    updateEnvironment(event.target.value as ReleaseEnvironment)
                  }
                >
                  <option value="DEVELOPMENT">Development</option>
                  <option value="STAGING">Staging</option>
                  <option value="PRODUCTION">Production</option>
                </select>
              </label>

              <label className="field field--wide">
                <span>Owner</span>
                <input
                  required
                  maxLength={120}
                  value={form.owner}
                  onChange={(event) => updateText('owner', event.target.value)}
                  placeholder="Platform Team"
                />
              </label>

              <label className="field field--full">
                <span>Description</span>
                <textarea
                  rows={3}
                  maxLength={2000}
                  value={form.description}
                  onChange={(event) => updateText('description', event.target.value)}
                  placeholder="What changes in this release?"
                />
              </label>
            </div>

            <div className="form-section-heading form-section-heading--checks">
              <div>
                <span>02</span>
                <strong>Readiness evidence</strong>
              </div>
              <div className="form-score">
                <strong>{score}%</strong>
                <span>current score</span>
              </div>
            </div>

            <div className="check-form-list">
              {checks.map((check) => (
                <label className="check-form-item" key={check.field}>
                  <input
                    type="checkbox"
                    checked={form[check.field]}
                    onChange={(event) => updateCheck(check.field, event.target.checked)}
                  />
                  <span className="custom-checkbox" aria-hidden="true">✓</span>
                  <span className="check-form-copy">
                    <strong>{check.label}</strong>
                    <small>{check.detail}</small>
                  </span>
                  <span className="check-weight">+{check.weight}</span>
                </label>
              ))}
            </div>

            <label className="field field--notes">
              <span>Deployment notes</span>
              <textarea
                rows={3}
                maxLength={4000}
                value={form.deployment_notes}
                onChange={(event) => updateText('deployment_notes', event.target.value)}
                placeholder="Runbook, change window, or deployment context"
              />
            </label>
          </div>

          <footer className="modal-footer">
            <button className="button button--secondary" type="button" onClick={onClose}>
              Cancel
            </button>
            <button className="button button--primary" type="submit" disabled={isSaving}>
              {isSaving ? 'Saving…' : release ? 'Save changes' : 'Create release'}
            </button>
          </footer>
        </form>
      </section>
    </div>
  )
}
