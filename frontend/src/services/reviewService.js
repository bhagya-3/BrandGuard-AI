
import { apiPatch, apiPost, apiRequest } from './apiClient.js'

export function runReview(documentId) {
  return apiPost(`/reviews/${encodeURIComponent(documentId)}/run`)
}

export function getReview(reviewId) {
  return apiRequest(`/reviews/${encodeURIComponent(reviewId)}`)
}

export function listReviews() {
  return apiRequest('/reviews/')
}

export function decideFinding(findingId, decision, suggestedText) {
  return apiPatch(`/findings/${encodeURIComponent(findingId)}/decision`, {
    decision,
    suggested_text: suggestedText,
  })
}

export function decideSuggestion(findingId, suggestionId, decision, suggestedText) {
  return apiPatch(
    `/findings/${encodeURIComponent(findingId)}/suggestions/${encodeURIComponent(suggestionId)}/decision`,
    {
      decision,
      suggested_text: suggestedText,
    }
  )
}

export function listComments(reviewId) {
  return apiRequest(`/comments/?review_id=${encodeURIComponent(reviewId)}`)
}

export function addComment(reviewId, body, findingId) {
  return apiPost('/comments/', { review_id: reviewId, body, finding_id: findingId })
}

export function requestApproval(reviewId) {
  return apiPost('/approvals/', { review_id: reviewId })
}
