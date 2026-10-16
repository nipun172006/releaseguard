export type ReleaseEnvironment = 'DEVELOPMENT' | 'STAGING' | 'PRODUCTION'

export type ReleaseStatus =
  | 'DRAFT'
  | 'READY'
  | 'DEPLOYING'
  | 'SUCCESS'
  | 'FAILED'
  | 'ROLLED_BACK'

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export type CheckField =
  | 'tests_passed'
  | 'security_scan_passed'
  | 'approval_received'
  | 'backup_confirmed'
  | 'rollback_plan_ready'

export type ReleaseRecord = {
  id: number
  application_name: string
  version: string
  environment: ReleaseEnvironment
  owner: string
  description: string | null
  status: ReleaseStatus
  tests_passed: boolean
  security_scan_passed: boolean
  approval_received: boolean
  backup_confirmed: boolean
  rollback_plan_ready: boolean
  deployment_notes: string | null
  created_at: string
  updated_at: string
  readiness_score: number
  risk_level: RiskLevel
  blockers: string[]
  is_ready: boolean
}

export type ReleaseStats = {
  total_releases: number
  ready_to_deploy: number
  active_deployments: number
  high_or_critical_risk: number
  successful_deployments: number
  average_readiness_score: number
}

export type ReleasePayload = {
  application_name: string
  version: string
  environment: ReleaseEnvironment
  owner: string
  description: string | null
  tests_passed: boolean
  security_scan_passed: boolean
  approval_received: boolean
  backup_confirmed: boolean
  rollback_plan_ready: boolean
  deployment_notes: string | null
}

export type ReleaseUpdate = Partial<ReleasePayload> & {
  status?: ReleaseStatus
}

export type ReleaseFilters = {
  search: string
  environment: '' | ReleaseEnvironment
  status: '' | ReleaseStatus
  risk: '' | RiskLevel
}
