import { apiRequest } from './apiClient.js'
import { listApprovals } from './approvalService.js'
import { listDocuments } from './documentService.js'
import { listReviews } from './reviewService.js'

export function listAuditEvents(limit = 100) {
  return apiRequest(`/audit/?limit=${encodeURIComponent(limit)}`)
}

export async function getWorkspaceAnalytics() {
  const [documents, reviews, approvals] = await Promise.all([
    listDocuments(),
    listReviews(),
    listApprovals(),
  ])
  const documentRows = Array.isArray(documents) ? documents : []
  const reviewRows = Array.isArray(reviews) ? reviews : []
  const approvalRows = Array.isArray(approvals) ? approvals : []
  const openFindings = reviewRows.reduce(
    (count, review) => count + (review.findings || []).filter((finding) => finding.status === 'open').length,
    0,
  )

  return {
    documents: documentRows.length,
    reviews: reviewRows.length,
    approvalsPending: approvalRows.filter((approval) => approval.status === 'pending').length,
    openFindings,
    recentReviews: reviewRows.slice(0, 10),
    documentsByStatus: documentRows.reduce((result, document) => {
      result[document.status] = (result[document.status] || 0) + 1
      return result
    }, {}),
    approvals: approvalRows,
  }
}
