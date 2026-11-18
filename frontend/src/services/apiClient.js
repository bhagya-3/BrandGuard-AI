const frontendHost = typeof window === 'undefined' ? 'localhost' : window.location.hostname
const frontendProtocol = typeof window !== 'undefined' && window.location.protocol === 'https:'
  ? 'https:'
  : 'http:'
const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL
  || `${frontendProtocol}//${frontendHost}:8000/api/v1`
const API_BASE_URL = configuredBaseUrl.replace(/\/+$/, '')
const TOKEN_KEY = 'brandguard_access_token'

export class ApiError extends Error {
  constructor(message, { status = 0, details = null } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.details = details
  }
}

export function getAccessToken() {
  return typeof window === 'undefined' ? null : window.localStorage.getItem(TOKEN_KEY)
}

export function setAccessToken(token) {
  if (typeof window === 'undefined') return
  if (token) window.localStorage.setItem(TOKEN_KEY, token)
  else window.localStorage.removeItem(TOKEN_KEY)
}

async function readPayload(response) {
  if (response.status === 204) return null
  const contentType = response.headers.get('content-type') || ''
  if (contentType.includes('application/json')) {
    try {
      return await response.json()
    } catch {
      throw new ApiError('The server returned invalid JSON.', { status: response.status })
    }
  }
  return response.text()
}

function getErrorMessage(payload, response) {
  const detail = payload && typeof payload === 'object'
    ? payload.detail || payload.message
    : payload
  if (Array.isArray(detail)) return detail.map((item) => item.msg || String(item)).join(', ')
  if (typeof detail === 'string' && detail.trim()) return detail
  return response.statusText || `Request failed (${response.status}).`
}

export async function apiRequest(path, options = {}) {
  if (typeof path !== 'string' || !path.startsWith('/')) {
    throw new TypeError('API paths must be absolute paths beginning with "/".')
  }

  const headers = new Headers(options.headers || {})
  const token = getAccessToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
    })
  } catch (error) {
    const reason = error instanceof Error ? ` ${error.message}` : ''
    throw new ApiError(
      `Could not connect to the BrandGuard API at ${API_BASE_URL}. Check that the backend is running and the API URL is correct.${reason}`,
    )
  }
  const payload = await readPayload(response)

  if (!response.ok) {
    throw new ApiError(getErrorMessage(payload, response), {
      status: response.status,
      details: payload,
    })
  }
  return payload
}

export const apiGet = (path, options = {}) => apiRequest(path, options)

export function apiPost(path, body, options = {}) {
  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData
  const headers = new Headers(options.headers || {})
  if (body !== undefined && !isFormData && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  return apiRequest(path, {
    ...options,
    method: 'POST',
    headers,
    body: body === undefined ? undefined : isFormData ? body : JSON.stringify(body),
  })
}

export function apiPatch(path, body, options = {}) {
  const headers = new Headers(options.headers || {})
  if (!headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
  return apiRequest(path, {
    ...options,
    method: 'PATCH',
    headers,
    body: JSON.stringify(body),
  })
}

export function apiDelete(path, options = {}) {
  return apiRequest(path, { ...options, method: 'DELETE' })
}
