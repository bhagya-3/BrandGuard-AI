import { Component, useState } from 'react'
import { Link, Navigate, useLocation } from 'react-router-dom'
import brandMark from '../assets/brandguard-mark.svg'
import useAuth from '../hooks/useAuth.js'
import useNotifications from '../hooks/useNotifications.js'
import { NAVIGATION_GROUPS } from '../utils/constants.js'
import { formatDateTime, formatFileSize, formatStatus, initials } from '../utils/formatters.js'
import { hasMinimumRole } from '../utils/permissions.js'

export function BrandLogo({ compact = false }) {
  return (
    <Link className={`brand-lockup ${compact ? 'brand-lockup-compact' : ''}`} to="/dashboard" aria-label="BrandGuard AI home">
      <img src={brandMark} alt="" width="34" height="34" />
      {!compact && <span>brandguard<span className="brand-ai">ai</span></span>}
    </Link>
  )
}

export function LoadingSpinner({ label = 'Loading', fullScreen = false }) {
  return (
    <div className={`loading-state ${fullScreen ? 'loading-fullscreen' : ''}`} role="status" aria-live="polite">
      <span className="loading-spinner" aria-hidden="true" />
      <span>{label}…</span>
    </div>
  )
}

export function PageHeader({ title, description, action, eyebrow = 'BRANDGUARD AI' }) {
  return (
    <header className="route-page-header">
      <div>
        {eyebrow && <span className="eyebrow">{eyebrow}</span>}
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action && <div className="route-page-action">{action}</div>}
    </header>
  )
}

export function Breadcrumbs({ items = [] }) {
  return (
    <nav className="breadcrumbs" aria-label="Breadcrumb">
      {items.map((item, index) => (
        <span key={`${item.label}-${index}`}>
          {index > 0 && <span className="breadcrumb-separator" aria-hidden="true">/</span>}
          {item.href && index < items.length - 1
            ? <Link to={item.href}>{item.label}</Link>
            : <span aria-current={index === items.length - 1 ? 'page' : undefined}>{item.label}</span>}
        </span>
      ))}
    </nav>
  )
}

export function Footer() {
  return (
    <footer className="route-footer">
      <div className="footer-main">
        <div className="footer-brand">
          <Link className="brand-lockup" to="/" aria-label="BrandGuard AI home">
            <img src={brandMark} alt="" width="34" height="34" />
            <span>brandguard<span className="brand-ai">ai</span></span>
          </Link>
          <p>Keep every story on brand with evidence-led reviews and people in control.</p>
          <span className="footer-trust"><span aria-hidden="true">✓</span> Human-led decisions, always</span>
        </div>
        <nav className="footer-column" aria-label="Product links">
          <h2>Product</h2>
          <Link to="/features">Features</Link>
          <Link to="/how-it-works">How it works</Link>
          <Link to="/login">Workspace sign in</Link>
        </nav>
        <nav className="footer-column" aria-label="Company links">
          <h2>Company</h2>
          <Link to="/about">About BrandGuard</Link>
          <Link to="/contact">Contact</Link>
          <Link to="/terms">Terms of use</Link>
        </nav>
        <nav className="footer-column" aria-label="Trust and privacy links">
          <h2>Trust</h2>
          <Link to="/security-info">Security</Link>
          <Link to="/privacy-policy">Privacy</Link>
        </nav>
      </div>
      <div className="footer-bottom">
        <span>© {new Date().getFullYear()} BrandGuard AI. All rights reserved.</span>
        <span>Evidence-backed reviews · Human approval</span>
      </div>
    </footer>
  )
}

export function Navbar() {
  const { user, isAuthenticated, signOut } = useAuth()
  return (
    <header className="public-navbar">
      <BrandLogo />
      <nav aria-label="Main navigation">
        <Link to="/features">Features</Link>
        <Link to="/how-it-works">How it works</Link>
        <Link to="/security-info">Security</Link>
      </nav>
      <div className="navbar-actions">
        {isAuthenticated
          ? <><Link className="button button-secondary" to="/dashboard">Workspace</Link><button className="text-button" onClick={signOut}>Sign out</button></>
          : <><Link className="text-button" to="/login">Sign in</Link><Link className="button button-primary" to="/register">Get started</Link></>}
        {user && <span className="user-avatar" title={user.full_name || user.email}>{initials(user.full_name || user.email)}</span>}
      </div>
    </header>
  )
}

export function Sidebar({ admin = false }) {
  const { user, signOut } = useAuth()
  const location = useLocation()
  const groups = admin
    ? [{ label: 'Administration', items: [
      { label: 'Admin dashboard', href: '/admin/admin-dashboard', icon: '▦' },
      { label: 'Users', href: '/admin/user-management', icon: '♧' },
      { label: 'Roles', href: '/admin/role-management', icon: '♙' },
      { label: 'Organization', href: '/admin/organization-settings', icon: '▣' },
      { label: 'Security logs', href: '/admin/security-logs', icon: '⌑' },
      { label: 'System health', href: '/admin/system-health', icon: '◉' },
    ] }]
    : NAVIGATION_GROUPS

  return (
    <aside className="workspace-sidebar">
      <BrandLogo />
      <div className="workspace-label">
        <span className="workspace-dot">{initials(user?.organization_name || 'Brand')}</span>
        <span><strong>{user?.organization_name || 'Brand workspace'}</strong><small>{user?.email}</small></span>
      </div>
      <nav aria-label="Workspace navigation">
        {groups.map((group) => (
          <div className="sidebar-nav-group" key={group.label}>
            <span className="nav-caption">{group.label}</span>
            {group.items.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className={`workspace-nav-item ${location.pathname === item.href || location.pathname.startsWith(`${item.href}/`) ? 'selected' : ''}`}
                aria-current={location.pathname === item.href ? 'page' : undefined}
              >
                <span className="app-icon" aria-hidden="true">{item.icon}</span>{item.label}
              </Link>
            ))}
          </div>
        ))}
        {admin && <Link className="workspace-nav-item" to="/dashboard">← Back to workspace</Link>}
      </nav>
      <div className="sidebar-bottom">
        <div className="signed-in">
          <span className="user-avatar">{initials(user?.full_name || user?.email)}</span>
          <span><strong>{user?.full_name || user?.email}</strong><small>{user?.role || 'Workspace member'}</small></span>
          <button aria-label="Sign out" title="Sign out" onClick={signOut}>↪</button>
        </div>
      </div>
    </aside>
  )
}

export function NotificationBell() {
  const [open, setOpen] = useState(false)
  const { notifications, unreadCount, markRead, markAllRead } = useNotifications()
  return (
    <div className="notification-bell-wrap">
      <button className="icon-button notification-bell" aria-label={`Notifications (${unreadCount} unread)`} aria-expanded={open} onClick={() => setOpen((value) => !value)}>
        ♧{unreadCount > 0 && <span className="notification-count">{unreadCount}</span>}
      </button>
      {open && <section className="notification-popover" aria-label="Notifications">
        <header><strong>Notifications</strong><button className="text-button" onClick={markAllRead}>Mark all read</button></header>
        {!notifications.length && <p className="muted">You’re all caught up.</p>}
        {notifications.slice(0, 6).map((item) => (
          <article className={`notification-item ${item.read ? '' : 'notification-unread'}`} key={item.id}>
            <div><strong>{item.title}</strong><p>{item.message}</p><small>{formatDateTime(item.created_at)}</small></div>
            {!item.read && <button className="text-button" onClick={() => markRead(item.id)}>Mark read</button>}
          </article>
        ))}
      </section>}
    </div>
  )
}

export function ProtectedRoute({ children, minimumRole }) {
  const { isAuthenticated, loading } = useAuth()
  const location = useLocation()
  if (loading) return <LoadingSpinner fullScreen label="Restoring your session" />
  if (!isAuthenticated) return <Navigate to="/login" replace state={{ from: location }} />
  if (minimumRole) {
    const { user } = useAuth()
    if (!hasMinimumRole(user, minimumRole)) return <Navigate to="/unauthorized" replace />
  }
  return children
}

export function ConfirmDialog({ open, title, children, confirmLabel = 'Confirm', onConfirm, onCancel, danger = false }) {
  if (!open) return null
  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={(event) => event.target === event.currentTarget && onCancel?.()}>
      <section className="dialog-card" role="dialog" aria-modal="true" aria-labelledby="confirm-title">
        <h2 id="confirm-title">{title}</h2><div>{children}</div>
        <div className="dialog-actions">
          <button className="button button-secondary" onClick={onCancel}>Cancel</button>
          <button className={`button ${danger ? 'button-danger' : 'button-primary'}`} onClick={onConfirm}>{confirmLabel}</button>
        </div>
      </section>
    </div>
  )
}

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    this.props.onError?.(error, info)
  }

  render() {
    if (this.state.error) {
      return <main className="error-boundary"><h1>Something went wrong</h1><p>{this.state.error.message}</p><button className="button button-primary" onClick={() => this.setState({ error: null })}>Try again</button></main>
    }
    return this.props.children
  }
}

export function FormError({ children, id }) {
  return children ? <p className="field-error" id={id} role="alert">{children}</p> : null
}

export function FormInput({ label, id, error, hint, ...props }) {
  const inputId = id || props.name
  return (
    <label className="form-field" htmlFor={inputId}>
      <span>{label}</span>
      <input id={inputId} aria-invalid={Boolean(error)} aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined} {...props} />
      {hint && !error && <small id={`${inputId}-hint`}>{hint}</small>}
      <FormError id={`${inputId}-error`}>{error}</FormError>
    </label>
  )
}

export function FormSelect({ label, id, options = [], error, ...props }) {
  const selectId = id || props.name
  return (
    <label className="form-field" htmlFor={selectId}>
      <span>{label}</span>
      <select id={selectId} aria-invalid={Boolean(error)} {...props}>
        {options.map((option) => typeof option === 'string'
          ? <option value={option} key={option}>{formatStatus(option)}</option>
          : <option value={option.value} key={option.value}>{option.label}</option>)}
      </select>
      <FormError>{error}</FormError>
    </label>
  )
}

export function DocumentStatusBadge({ status }) {
  return <span className={`status-tag status-${status || 'unknown'}`}>{formatStatus(status || 'unknown')}</span>
}

export function FileUploader({ onFile, busy = false, accept, maxSizeLabel = 'Maximum upload size is set by your workspace.' }) {
  const [error, setError] = useState('')
  return (
    <div className="file-uploader">
      <label className="upload-dropzone">
        <input type="file" accept={accept} disabled={busy} onChange={(event) => {
          const file = event.target.files?.[0]
          console.log('[BrandGuard] File selected:', file?.name, file?.size)
          if (file) {
            setError('')
            Promise.resolve(onFile?.(file)).catch((uploadError) => setError(uploadError.message))
          }
          event.target.value = ''
        }} />
        <span className="upload-icon">↑</span><strong>{busy ? 'Uploading…' : 'Choose a file or drop it here'}</strong><small>{maxSizeLabel}</small>
      </label>
      <FormError>{error}</FormError>
    </div>
  )
}

export function FilePreview({ file }) {
  if (!file) return <div className="empty-inline">No file selected.</div>
  return <div className="file-preview"><span className="file-icon">▤</span><div><strong>{file.name || file.original_filename || file.title}</strong><small>{formatFileSize(file.size ?? file.file_size)}</small></div></div>
}

export function DocumentMetadata({ document }) {
  if (!document) return null
  const metadata = [
    ['Filename', document.original_filename],
    ['Type', document.mime_type],
    ['Size', formatFileSize(document.file_size)],
    ['Version', document.current_version],
    ['Created', formatDateTime(document.created_at)],
  ].filter(([, value]) => value !== null && value !== undefined)
  return <dl className="metadata-list">{metadata.map(([label, value]) => <div key={label}><dt>{label}</dt><dd>{value}</dd></div>)}</dl>
}

export function FileVersionHistory({ versions = [] }) {
  if (!versions.length) return <p className="muted">No version history is available.</p>
  return <ol className="timeline-list">{versions.map((version) => <li key={version.id}><strong>Version {version.version_number || version.version || '—'}</strong><small>{formatDateTime(version.created_at)}</small><p>{version.change_note || version.original_filename || 'Uploaded version'}</p></li>)}</ol>
}

export function StatCard({ label, value, detail, trend }) {
  return <article className="stat-card"><span>{label}</span><strong>{value ?? '—'}</strong>{detail && <small>{detail}</small>}{trend && <em>{trend}</em>}</article>
}

export function ActivityChart({ data = [] }) {
  const maximum = Math.max(1, ...data.map((item) => Number(item.value) || 0))
  return <div className="activity-chart" role="img" aria-label="Activity summary">
    {data.length ? data.map((item) => <div key={item.label} className="activity-bar-wrap"><span>{item.value}</span><div className="activity-bar" style={{ height: `${Math.max(4, ((Number(item.value) || 0) / maximum) * 100)}%` }} /><small>{item.label}</small></div>) : <p className="muted">Activity data will appear as reviews are completed.</p>}
  </div>
}

export function RecentReviews({ reviews = [] }) {
  return <div className="compact-list">{reviews.slice(0, 5).map((item) => <Link key={item.id} to={`/reviews/${item.id}`}><span><strong>{item.document_title || item.document?.title || 'Content review'}</strong><small>{formatDateTime(item.created_at)}</small></span><DocumentStatusBadge status={item.status} /></Link>)}</div>
}

export function PendingApprovals({ approvals = [] }) {
  const pending = approvals.filter((item) => item.status === 'pending')
  return <div className="compact-list">{pending.slice(0, 5).map((item) => <Link key={item.id} to={`/approvals/${item.id}`}><span><strong>{item.document_title || 'Approval request'}</strong><small>Requested {formatDateTime(item.requested_at || item.created_at)}</small></span><DocumentStatusBadge status={item.status} /></Link>)}{!pending.length && <p className="muted">No pending approvals.</p>}</div>
}

export function IssueCard({ finding, onDecision }) {
  return <article className="finding-row">
    <div className="finding-meta"><span className={`severity severity-${finding.severity}`}>{formatStatus(finding.severity || 'low')}</span><span>{formatStatus(finding.category || 'general')}</span></div>
    <h3>{finding.title || 'Review finding'}</h3><p>{finding.description}</p>
    <EvidencePanel evidence={finding.evidence || []} />
    {onDecision && finding.status === 'open' && <div className="finding-actions"><button className="button button-secondary" onClick={() => onDecision(finding, 'dismissed')}>Dismiss</button><button className="button button-primary" onClick={() => onDecision(finding, 'resolved')}>Resolve</button></div>}
  </article>
}

export function IssueFilters({ value, onChange }) {
  return <div className="filter-row">
    <label>Severity<select value={value.severity} onChange={(event) => onChange({ ...value, severity: event.target.value })}><option value="all">All severities</option><option>critical</option><option>high</option><option>medium</option><option>low</option></select></label>
    <label>Status<select value={value.status} onChange={(event) => onChange({ ...value, status: event.target.value })}><option value="all">All statuses</option><option value="open">Open</option><option value="resolved">Resolved</option><option value="dismissed">Dismissed</option></select></label>
  </div>
}

export function EvidencePanel({ evidence = [] }) {
  return <section className="evidence-panel"><h3>Evidence</h3>{evidence.length ? evidence.map((item, index) => <blockquote key={item.source_version_id || index}><p>{item.quote || item.quoted_text || item.source_reference}</p><small>{item.source_title || item.source_id || item.source_reference || 'Approved source'}{item.relevance_score != null ? ` · ${Math.round(item.relevance_score * 100)}% match` : ''}</small></blockquote>) : <p className="muted">No supporting evidence is attached.</p>}</section>
}

export function ConfidenceIndicator({ value }) {
  const score = Math.max(0, Math.min(1, Number(value) || 0))
  return <span className="confidence-indicator" aria-label={`${Math.round(score * 100)} percent confidence`}><span style={{ width: `${score * 100}%` }} />{Math.round(score * 100)}%</span>
}

export function OriginalContent({ content }) {
  return <section className="content-card"><h2>Original content</h2><pre className="original-content">{content || 'No extracted text is available for this document.'}</pre></section>
}

export function SuggestedCorrection({ suggestion, onApply }) {
  if (!suggestion) return null
  return <section className="suggestion-box"><h3>Suggested correction</h3><p>{suggestion.suggested_text}</p>{suggestion.rationale && <small>{suggestion.rationale}</small>}{onApply && <button className="button button-secondary" onClick={() => onApply(suggestion.suggested_text)}>Use suggestion for this review</button>}</section>
}

export function ComparisonView({ before = '', after = '' }) {
  return <div className="comparison-view"><section><h3>Original</h3><pre>{before || 'No original text provided.'}</pre></section><section><h3>Proposed</h3><pre>{after || 'No revised text provided.'}</pre></section></div>
}

export function ReviewComments({ comments = [], onSubmit, disabled = false }) {
  const [body, setBody] = useState('')
  return <section className="content-card"><h2>Discussion</h2><div className="comment-list">{comments.map((comment) => <article className="comment-item" key={comment.id}><strong>{comment.author || 'Workspace member'}</strong><p>{comment.body}</p><small>{formatDateTime(comment.created_at)}</small></article>)}{!comments.length && <p className="muted">No comments yet.</p>}</div>
    {onSubmit && <form className="comment-form" onSubmit={(event) => { event.preventDefault(); if (!body.trim()) return; onSubmit(body.trim()); setBody('') }}><label htmlFor="shared-review-comment">Add a comment</label><textarea id="shared-review-comment" value={body} onChange={(event) => setBody(event.target.value)} maxLength={5000} required /><button className="button button-primary" disabled={disabled || !body.trim()}>Post comment</button></form>}
  </section>
}

export function ReviewWorkspace({ review, comments = [], onComment, onDecision, busy = false }) {
  const findings = review?.findings || []
  return <div className="review-layout">
    <section className="content-card findings-card">
      <header className="card-heading"><div><h2>Review findings</h2><p>{findings.length} finding(s) · Human review is required before publication.</p></div><DocumentStatusBadge status={review?.status} /></header>
      {findings.length
        ? findings.map((finding) => <IssueCard key={finding.id} finding={finding} onDecision={onDecision && !busy ? onDecision : undefined} />)
        : <div className="empty-state"><h3>No findings recorded</h3><p>This review has no findings. Continue to approval when appropriate.</p></div>}
    </section>
    <aside><ReviewComments comments={comments} onSubmit={onComment} disabled={busy} /></aside>
  </div>
}

export function ApprovalStatus({ status }) {
  return <DocumentStatusBadge status={status} />
}

export function ApprovalTimeline({ events = [] }) {
  return <FileVersionHistory versions={events} />
}

export function ApprovalChecklist({ items = [] }) {
  return <ul className="checklist">{items.map((item, index) => <li key={item.id || item.label || index}><span aria-hidden="true">{item.complete ? '✓' : '○'}</span><span>{item.label || item.title}</span></li>)}</ul>
}

export function ReviewerAssignment({ reviewers = [], value, onChange }) {
  return <label className="form-field"><span>Assign reviewer</span><select value={value || ''} onChange={(event) => onChange?.(event.target.value)}><option value="">Unassigned</option>{reviewers.map((reviewer) => <option value={reviewer.id} key={reviewer.id}>{reviewer.full_name || reviewer.email}</option>)}</select></label>
}

export function SignOffDialog(props) {
  return <ConfirmDialog {...props} title={props.title || 'Sign off this review'} confirmLabel={props.confirmLabel || 'Confirm sign-off'} />
}

export function SourceCard({ source }) {
  return <article className="source-item"><span className="source-icon">▣</span><div><h3>{source.title}</h3><p>{source.description || formatStatus(source.source_type)}</p><small>{source.versions?.length || 0} version(s)</small></div><DocumentStatusBadge status={source.status} /></article>
}

export function SourceOwner({ owner }) {
  return <span className="source-owner"><span className="user-avatar">{initials(owner?.full_name || owner?.email)}</span>{owner?.full_name || owner?.email || 'Workspace'}</span>
}

export function SourceUploader({ onFile, busy }) {
  return <FileUploader onFile={onFile} busy={busy} accept=".pdf,.docx,.pptx,.txt,.png,.jpg,.jpeg,.webp" />
}

export function SourceVerification({ status, onApprove, busy = false }) {
  return <div className="verification-row"><DocumentStatusBadge status={status} />{onApprove && status !== 'approved' && <button className="button button-secondary" disabled={busy} onClick={onApprove}>Verify source</button>}</div>
}

export function SourceVersionHistory({ versions }) {
  return <FileVersionHistory versions={versions} />
}

export function PermissionGuard({ minimumRole, children, fallback = null }) {
  const { user } = useAuth()
  return hasMinimumRole(user, minimumRole) ? children : fallback
}

export function AccessDenied({ message = 'You do not have permission to view this page.' }) {
  return <section className="empty-state"><span className="empty-icon">⌑</span><h1>Access denied</h1><p>{message}</p><Link className="button button-primary" to="/dashboard">Return to workspace</Link></section>
}

export function SessionTimeout({ onSignIn }) {
  return <section className="notice notice-warning" role="status"><span>Your session has expired. Sign in again to continue.</span><button className="button button-secondary" onClick={onSignIn}>Sign in</button></section>
}

export function useProtectedRoute(minimumRole) {
  const auth = useAuth()
  const location = useLocation()
  if (auth.loading) return { allowed: false, redirect: null, loading: true }
  if (!auth.isAuthenticated) return { allowed: false, redirect: <Navigate to="/login" state={{ from: location }} replace />, loading: false }
  if (minimumRole && !hasMinimumRole(auth.user, minimumRole)) {
    return { allowed: false, redirect: <Navigate to="/unauthorized" replace />, loading: false }
  }
  return { allowed: true, redirect: null, loading: false }
}
