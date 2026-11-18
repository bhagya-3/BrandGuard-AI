export const APP_NAME = 'BrandGuard AI'
export const DEFAULT_PAGE_SIZE = 10
export const MAX_UPLOAD_SIZE_MB = 25
export const ACCEPTED_FILE_TYPES = '.pdf,.docx,.pptx,.png,.jpg,.jpeg,.webp,.txt'

export const DOCUMENT_STATUSES = [
  'uploaded',
  'processing',
  'processed',
  'in_review',
  'approved',
  'rejected',
  'archived',
]

export const FINDING_SEVERITIES = ['critical', 'high', 'medium', 'low']

export const NAVIGATION_GROUPS = [
  {
    label: 'Workspace',
    items: [
      { label: 'Overview', href: '/dashboard', icon: '⌂' },
      { label: 'Documents', href: '/documents', icon: '▤' },
      { label: 'Reviews', href: '/reviews', icon: '✓' },
      { label: 'Approvals', href: '/approvals', icon: '◷' },
      { label: 'Brand sources', href: '/sources', icon: '▣' },
    ],
  },
  {
    label: 'Manage',
    items: [
      { label: 'Team', href: '/workspace/team-members', icon: '♧' },
      { label: 'Analytics', href: '/analytics/analytics-dashboard', icon: '▥' },
      { label: 'Settings', href: '/settings/profile-settings', icon: '⚙' },
    ],
  },
]