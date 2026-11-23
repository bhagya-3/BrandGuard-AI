import { lazy } from 'react'

const pageModules = Object.fromEntries(
  Object.entries(import.meta.glob('../pages/**/*.jsx'))
    .filter(([modulePath]) => !modulePath.endsWith('/PageView.jsx')),
)

const pathOverrides = {
  'public/LandingPage': '/',
  'dashboard/DashboardPage': '/dashboard',
  'dashboard/MyActivityPage': '/dashboard/my-activity',
  'dashboard/NotificationsPage': '/notifications',
  'documents/AllDocumentsPage': '/documents',
  'documents/ArchivedDocumentsPage': '/documents/archived',
  'documents/DocumentDetailsPage': '/documents/:id',
  'documents/DocumentVersionsPage': '/documents/:id/versions',
  'documents/UploadDocumentPage': '/documents/upload',
  'approvals/ApprovalDetailsPage': '/approvals/:id',
  'approvals/ApprovalInboxPage': '/approvals',
  'approvals/ChangesRequestedPage': '/approvals/changes-requested',
  'approvals/MyAssignedReviewsPage': '/reviews/assigned',
  'approvals/PublicationHistoryPage': '/approvals/publication-history',
  'approvals/SignOffPage': '/approvals/:id/sign-off',
  'review/CompareVersionsPage': '/reviews/compare',
  'review/ReviewCommentsPage': '/reviews/:id/comments',
  'review/ReviewDetailsPage': '/reviews/:id',
  'review/ReviewHistoryPage': '/reviews/history',
  'review/ReviewResultsPage': '/reviews',
  'review/StartReviewPage': '/reviews/start',
  'sources/AddSourcePage': '/sources/add',
  'sources/ClaimsRegisterPage': '/sources/claims',
  'sources/FactSheetsPage': '/sources/fact-sheets',
  'sources/SourceConflictsPage': '/sources/conflicts',
  'sources/SourceDetailsPage': '/sources/:id',
  'sources/SourceRegisterPage': '/sources',
  'sources/TerminologyPage': '/sources/terminology',
  'sources/VisualLibraryPage': '/sources/visual-library',
  'workspace/DepartmentsPage': '/workspace/departments',
  'workspace/InvitationsPage': '/workspace/invitations',
  'workspace/TeamMembersPage': '/workspace/team-members',
'workspace/TeamMemberDetailsPage': '/workspace/team-members/:id',
'workspace/WorkspacePage': '/workspace',
}

function kebabCase(value) {
  return value
    .replace(/Page$/, '')
    .replace(/([a-z0-9])([A-Z])/g, '$1-$2')
    .replace(/([A-Z])([A-Z][a-z])/g, '$1-$2')
    .toLowerCase()
}

function pathFor(key) {
  if (pathOverrides[key]) return pathOverrides[key]
  const [group, file] = key.split('/')
  const slug = kebabCase(file)
  if (group === 'public') return `/${slug}`
  if (group === 'auth') return `/${slug}`
  if (group === 'errors') return `/${slug}`
  return `/${group}/${slug}`
}

function categoryFor(group) {
  if (group === 'public') return 'public'
  if (group === 'auth') return 'auth'
  if (group === 'errors') return 'errors'
  return group === 'admin' ? 'admin' : 'workspace'
}

export const routeConfig = Object.entries(pageModules).map(([modulePath, importer]) => {
  const key = modulePath.replace('../pages/', '').replace(/\.jsx$/, '')
  const [group] = key.split('/')
  return {
    key,
    path: pathFor(key),
    category: categoryFor(group),
    minimumRole: group === 'admin' ? 'admin' : null,
    Component: lazy(importer),
  }
})

export const publicRoutes = routeConfig.filter((route) => route.category === 'public')
export const authRoutes = routeConfig.filter((route) => route.category === 'auth')
export const errorRoutes = routeConfig.filter((route) => route.category === 'errors')
export const adminRoutes = routeConfig.filter((route) => route.category === 'admin')
export const workspaceRoutes = routeConfig.filter((route) => route.category === 'workspace')