import { apiPost, apiRequest } from './apiClient.js'

export function listDocuments() {
  return apiRequest('/documents/')
}

export function getDocument(documentId) {
  return apiRequest(`/documents/${encodeURIComponent(documentId)}`)
}

export function uploadDocument(file, workspaceId) {
  const body = new FormData()
  body.append('file', file)
  if (workspaceId) body.append('workspace_id', workspaceId)
  return apiPost('/documents/upload', body)
}

export function archiveDocument(documentId) {
  return apiRequest(`/documents/${encodeURIComponent(documentId)}/archive`, { method: 'POST' })
}

export function listDocumentVersions(documentId) {
  return apiRequest(`/documents/${encodeURIComponent(documentId)}/versions`)
}