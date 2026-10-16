import type {
  ReleaseFilters,
  ReleasePayload,
  ReleaseRecord,
  ReleaseStats,
  ReleaseUpdate,
} from './types'

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type ValidationIssue = {
  msg?: string
}

type ErrorBody = {
  detail?: string | ValidationIssue[]
}

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`

    try {
      const body = (await response.json()) as ErrorBody
      if (typeof body.detail === 'string') {
        message = body.detail
      } else if (Array.isArray(body.detail)) {
        message = body.detail.map((issue) => issue.msg).filter(Boolean).join(' ')
      }
    } catch {
      // Keep the status-based fallback when a response is not JSON.
    }

    throw new ApiError(message, response.status)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export function getApiBaseUrl(): string {
  return apiBaseUrl
}

export function getHealth(signal?: AbortSignal): Promise<{ status: string }> {
  return request('/health', { signal })
}

export function getStats(signal?: AbortSignal): Promise<ReleaseStats> {
  return request('/api/releases/stats', { signal })
}

export function getReleases(
  filters: ReleaseFilters,
  signal?: AbortSignal,
): Promise<ReleaseRecord[]> {
  const parameters = new URLSearchParams()

  if (filters.search.trim()) {
    parameters.set('search', filters.search.trim())
  }
  if (filters.environment) {
    parameters.set('environment', filters.environment)
  }
  if (filters.status) {
    parameters.set('status', filters.status)
  }
  if (filters.risk) {
    parameters.set('risk', filters.risk)
  }

  const query = parameters.size > 0 ? `?${parameters.toString()}` : ''
  return request(`/api/releases${query}`, { signal })
}

export function createRelease(payload: ReleasePayload): Promise<ReleaseRecord> {
  return request('/api/releases', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateRelease(
  releaseId: number,
  payload: ReleaseUpdate,
): Promise<ReleaseRecord> {
  return request(`/api/releases/${releaseId}`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  })
}

export function deleteRelease(releaseId: number): Promise<void> {
  return request(`/api/releases/${releaseId}`, { method: 'DELETE' })
}
