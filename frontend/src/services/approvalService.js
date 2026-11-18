import { apiPatch, apiPost, apiRequest } from './apiClient.js'

export function listApprovals() {
  return apiRequest('/approvals/')
}

export function decideApproval(approvalId, decision, decisionNote = '') {
  return apiPatch(`/approvals/${encodeURIComponent(approvalId)}/decision`, {
    decision,
    decision_note: decisionNote,
  })
}

export function createApproval(reviewId) {
  return apiPost('/approvals/', { review_id: reviewId })
}