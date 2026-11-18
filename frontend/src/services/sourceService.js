import { apiPost, apiRequest } from './apiClient.js'

export function listSources() {
  return apiRequest('/sources/')
}

export function createSource(source) {
  return apiPost('/sources/', source)
}

export function approveSourceVersion(sourceId, versionId) {
  return apiPost(`/sources/${encodeURIComponent(sourceId)}/versions/${encodeURIComponent(versionId)}/approve`)
}

export function getSource(sourceId) {
  return apiRequest(`/sources/${encodeURIComponent(sourceId)}`)
}