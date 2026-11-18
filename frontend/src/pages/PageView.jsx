import { useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom'
import { apiPost, apiRequest } from '../services/apiClient.js'
import { decideApproval } from '../services/approvalService.js'
import { getWorkspaceAnalytics } from '../services/analyticsService.js'
import { getDocument, listDocuments, uploadDocument } from '../services/documentService.js'
import {
  addComment,
  decideFinding,
  getReview,
  listComments,
  listReviews,
  requestApproval,
  runReview,
} from '../services/reviewService.js'
import { approveSourceVersion, createSource, getSource, listSources } from '../services/sourceService.js'
import {
  changePassword,
  requestPasswordReset,
  resetPassword,
  verifyEmail,
} from '../services/authService.js'
import {
  getNotificationPreferences,
  saveNotificationPreferences,
} from '../services/notificationPreferenceService.js'
import { AuthContext } from '../context/AuthContext.jsx'
import { NotificationContext } from '../context/NotificationContext.jsx'
import { WorkspaceContext } from '../context/WorkspaceContext.jsx'
import {
  ActivityChart,
  DocumentMetadata,
  DocumentStatusBadge,
  EvidencePanel,
  FileUploader,
  LoadingSpinner,
  PageHeader,
  ReviewWorkspace,
  StatCard,
} from '../components/shared.jsx'
import { acceptedFileTypes, validateUploadFile } from '../utils/fileHelpers.js'
import { formatDateTime, formatStatus, titleFromKey } from '../utils/formatters.js'

const publicCopy = {
  'public/LandingPage': {
    title: 'Protect your brand in every piece of content',
    description: 'Review content against approved brand guidance, keep decisions evidence-backed, and make final approval a human responsibility.',
    bullets: ['One workspace for documents and reviews', 'Findings tied to approved source material', 'Clear decisions and an auditable approval path'],
  },
  'public/AboutPage': {
    title: 'About BrandGuard AI',
    description: 'BrandGuard helps teams apply their brand standards consistently while keeping people in control of important decisions.',
    bullets: ['Organization-scoped workspaces', 'Traceable review findings', 'Human-led approval and publishing'],
  },
  'public/FeaturesPage': {
    title: 'Tools for confident content review',
    description: 'Bring content, trusted references, reviewers, and decisions together in one clear workflow.',
    bullets: ['Document intake and text extraction', 'Deterministic terminology and claims checks', 'Comments, approvals, and audit history'],
  },
  'public/HowItWorksPage': {
    title: 'A practical review workflow',
    description: 'Move from an uploaded draft to an accountable review without silently changing or publishing content.',
    bullets: ['Upload a supported document', 'Inspect findings and their supporting context', 'Resolve issues and request another person’s approval'],
  },
  'public/SecurityInfoPage': {
    title: 'Security is part of the workflow',
    description: 'BrandGuard scopes content to an organization and records review and approval actions for later inspection.',
    bullets: ['Organization-aware API access', 'Protected review history', 'Local storage and deployment settings controlled by your organization'],
  },
  'public/PrivacyPolicyPage': {
    title: 'Privacy information',
    description: 'Your organization controls the content and infrastructure configured for its BrandGuard deployment.',
    bullets: ['Only upload content you are authorized to process', 'Optional external AI integrations are controlled by deployment configuration', 'Contact your workspace administrator for data retention details'],
  },
  'public/TermsPage': {
    title: 'Terms of use',
    description: 'Use BrandGuard as a decision-support tool, not as a substitute for legal, regulatory, or subject-matter review.',
    bullets: ['Review generated findings before acting on them', 'Keep approved source material current', 'A human reviewer remains responsible for approval and publication'],
  },
}

const resourceMessages = {
  admin: 'Administrative controls are ready in the frontend, but the current API does not expose this resource yet.',
  settings: 'These preferences are saved in this browser. Account and organization changes require corresponding API support.',
  publishing: 'Publishing actions are intentionally gated until the publishing API is enabled for this deployment.',
  analytics: 'Analytics are calculated from the documents, reviews, and approvals currently available to your account.',
}

function getGroup(pageKey) {
  return pageKey.split('/')[0]
}

async function loadPageData(pageKey, entityId) {
  const group = getGroup(pageKey)
  if (group === 'documents') {
    if (pageKey.includes('DocumentDetails') && entityId) return getDocument(entityId)
    if (pageKey.includes('DocumentVersions') && entityId) return apiRequest(`/documents/${encodeURIComponent(entityId)}/versions`)
    return listDocuments()
  }
  if (group === 'review') {
    if ((pageKey.includes('ReviewDetails') || pageKey.includes('ReviewComments')) && entityId) return getReview(entityId)
    return listReviews()
  }
  if (group === 'approvals') {
    const approvals = await apiRequest('/approvals/')
    if (!Array.isArray(approvals)) throw new Error('The server returned an invalid approval list.')
    if (pageKey.includes('ApprovalDetails') && entityId) {
    const approval = approvals.find((item) => item.id === entityId)
    if (!approval) throw new Error('Approval request not found.')
    return approval
    }
    return approvals
  }
  if (group === 'sources') {
    if (pageKey.includes('SourceDetails') && entityId) {
      try {
        return await getSource(entityId)
      } catch (error) {
        if (error.status !== 404 && error.status !== 405) throw error
        const sources = await listSources()
        if (!Array.isArray(sources)) throw new Error('The server returned an invalid source list.')
        const source = sources.find((item) => item.id === entityId)
        if (!source) throw new Error('Source not found.')
        return source
      }
    }
    return listSources()
  }
  if (group === 'workspace') return apiRequest('/workspaces/')
  if (group === 'analytics') return getWorkspaceAnalytics()
  if (group === 'dashboard') {
    const [documents, reviews, approvals] = await Promise.all([listDocuments(), listReviews(), apiRequest('/approvals/')])
    return { documents, reviews, approvals }
  }
  return null
}

function getDescription(group, title) {
  const descriptions = {
    documents: 'Manage content submitted to your organization for review.',
    approvals: 'Review sign-off requests and keep the decision trail clear.',
    review: 'Inspect findings, approved evidence, and reviewer discussion.',
    sources: 'Maintain the reference material used to ground content reviews.',
    workspace: 'Manage workspace information and team access.',
    analytics: 'Understand review activity and the issues that need attention.',
    settings: 'Manage your personal preferences and account security.',
    admin: 'Manage organization controls and operational visibility.',
    publishing: 'Prepare and inspect content that has completed review.',
    dashboard: 'A current view of your workspace review activity.',
  }
  return descriptions[group] || `${title} for your BrandGuard workspace.`
}

function rowsFrom(data) {
  if (Array.isArray(data)) return data
  if (data && typeof data === 'object') return [data]
  return []
}

function entityHref(group, row) {
  if (!row?.id) return null
  if (group === 'documents') return `/documents/${row.id}`
  if (group === 'review') return `/reviews/${row.id}`
  if (group === 'approvals') return `/approvals/${row.id}`
  if (group === 'sources') return `/sources/${row.id}`
  return null
}

function EmptyState({ title, text, action }) {
  return <section className="empty-state"><span className="empty-icon">✳</span><h2>{title}</h2><p>{text}</p>{action}</section>
}

function DataTable({ rows, group, onRunReview, onApprovalDecision, busy }) {
  if (!rows.length) return <EmptyState title="Nothing here yet" text="New workspace activity will appear here when it is available." />
  const columns = group === 'documents'
    ? ['Content', 'Status', 'Findings', 'Updated']
    : group === 'approvals'
      ? ['Request', 'Status', 'Requested', 'Decision']
      : group === 'sources'
        ? ['Source', 'Type', 'Status', 'Updated']
        : group === 'review'
          ? ['Review', 'Status', 'Findings', 'Created']
          : ['Name', 'Description', 'Updated']

  return <div className="table-scroll"><table className="data-table">
    <thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}<th>Action</th></tr></thead>
    <tbody>{rows.map((row) => {
      const title = row.title || row.document_title || row.document?.title || row.name || row.original_filename || 'Untitled'
      const href = entityHref(group, row)
      return <tr key={row.id || title}>
        <td>{href ? <Link className="table-primary-link" to={href}><strong>{title}</strong></Link> : <strong>{title}</strong>}<small>{row.original_filename || row.description || row.source_type || row.requester || ''}</small></td>
        <td><DocumentStatusBadge status={row.status} /></td>
        <td>{group === 'documents' ? row.finding_count ?? '—' : group === 'approvals' ? row.requester || '—' : group === 'sources' ? formatStatus(row.source_type || 'reference') : (row.findings || []).length || '—'}</td>
        <td>{formatDateTime(row.updated_at || row.requested_at || row.created_at)}</td>
        <td><div className="table-actions">
          {group === 'documents' && <button className="text-button" disabled={busy} onClick={() => onRunReview(row)}>Run review</button>}
          {group === 'approvals' && row.status === 'pending' && <>
            <button className="text-button" disabled={busy} onClick={() => onApprovalDecision(row, 'rejected')}>Request changes</button>
            <button className="text-button" disabled={busy} onClick={() => onApprovalDecision(row, 'approved')}>Approve</button>
          </>}
          {href && <Link className="row-open" to={href} aria-label={`Open ${title}`}>→</Link>}
        </div></td>
      </tr>
    })}</tbody>
  </table></div>
}

function AuthPage({ pageKey }) {
  const { signIn, signUp, loading, error: authError } = useContext(AuthContext)
  const navigate = useNavigate()
  const location = useLocation()
  const [formError, setFormError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const isRegister = pageKey.endsWith('RegisterPage')
  const isForgot = pageKey.endsWith('ForgotPasswordPage')
  const isReset = pageKey.endsWith('ResetPasswordPage')
  const isVerify = pageKey.endsWith('VerifyEmailPage')
  const isTwoFactor = pageKey.endsWith('TwoFactorPage')
  const isInvitation = pageKey.endsWith('AcceptInvitationPage')
  const title = isForgot ? 'Reset your password'
    : isReset ? 'Choose a new password'
      : isVerify ? 'Verify your email'
        : isTwoFactor ? 'Two-step verification'
          : isInvitation ? 'Accept your invitation'
            : isRegister ? 'Create your workspace'
              : 'Welcome back'

  async function submit(event) {
    event.preventDefault()
    const values = Object.fromEntries(new FormData(event.currentTarget).entries())
    setFormError('')
    setSuccessMessage('')
    try {
      if (isForgot) {
        await requestPasswordReset(values.email)
        setSuccessMessage('If the address belongs to an account, password reset instructions will be sent.')
        return
      }
      if (isReset) {
        const token = values.token || new URLSearchParams(location.search).get('token') || ''
        await resetPassword(token, values.password)
        setSuccessMessage('Password updated. You can now sign in.')
        return
      }
      if (isVerify) {
        const token = values.token || new URLSearchParams(location.search).get('token') || ''
        await verifyEmail(token)
        setSuccessMessage('Email address verified.')
        return
      }
      if (isTwoFactor) {
        await apiPost('/auth/two-factor/verify', { code: values.code })
        navigate('/dashboard', { replace: true })
        return
      }
      if (isInvitation) {
        await apiPost('/auth/accept-invitation', {
          token: values.token,
          full_name: values.full_name,
          password: values.password,
        })
        navigate('/login', { replace: true })
        return
      }
      if (isRegister) {
        await signUp({
          full_name: values.full_name,
          organization_name: values.organization_name,
          email: values.email,
          password: values.password,
        })
      } else {
        await signIn({ email: values.email, password: values.password })
      }
      navigate(location.state?.from?.pathname || '/dashboard', { replace: true })
    } catch (requestError) {
      setFormError(requestError.message || 'The request could not be completed.')
    }
  }

  return <section className="auth-card">
    <span className="eyebrow">SECURE WORKSPACE</span>
    <h1>{title}</h1>
    <p className="muted">{isRegister ? 'Create an organization account to start reviewing content.' : isForgot ? 'Enter your email and we will request a reset link.' : isReset ? 'Use the reset token from your email to change your password.' : isVerify ? 'Use the verification token sent to your email address.' : isTwoFactor ? 'Enter the verification code from your authenticator.' : isInvitation ? 'Enter your invitation token to join the workspace.' : 'Sign in to continue to your organization’s review workspace.'}</p>
    {(formError || authError) && <div className="notice notice-error" role="alert">{formError || authError}</div>}
    {successMessage && <div className="notice notice-success" role="status">{successMessage}</div>}
    <form className="auth-form" onSubmit={submit}>
      {isRegister && <>
        <label>Full name<input name="full_name" autoComplete="name" minLength={2} required /></label>
        <label>Organization<input name="organization_name" autoComplete="organization" minLength={2} required /></label>
      </>}
      {(isRegister || !isReset && !isVerify && !isTwoFactor && !isInvitation) && <label>Work email<input name="email" type="email" autoComplete="email" required /></label>}
      {(isReset || isVerify || isInvitation) && <label>Token<input name="token" autoComplete="one-time-code" defaultValue={new URLSearchParams(location.search).get('token') || ''} required /></label>}
      {isInvitation && <label>Full name<input name="full_name" autoComplete="name" required /></label>}
      {isTwoFactor && <label>Verification code<input name="code" inputMode="numeric" autoComplete="one-time-code" minLength={6} maxLength={8} required /></label>}
      {(isRegister || isReset || isInvitation || !isForgot && !isVerify && !isTwoFactor) && <label>Password<input name="password" type="password" autoComplete={isRegister || isReset || isInvitation ? 'new-password' : 'current-password'} minLength={isRegister || isReset || isInvitation ? 12 : 1} required /></label>}
      {isRegister && <small className="muted">Use at least 12 characters.</small>}
      <button className="button button-primary full-width" disabled={loading}>{loading ? 'Please wait…' : isRegister ? 'Create account' : isForgot ? 'Request reset link' : isReset ? 'Update password' : isVerify ? 'Verify email' : isTwoFactor ? 'Verify code' : isInvitation ? 'Accept invitation' : 'Sign in'}</button>
    </form>
    {(isRegister || pageKey.endsWith('LoginPage')) && <p className="auth-caption">{isRegister ? 'Already have an account?' : 'New to BrandGuard?'} <Link to={isRegister ? '/login' : '/register'}>{isRegister ? 'Sign in' : 'Create an account'}</Link></p>}
    {!isRegister && pageKey.endsWith('LoginPage') && <Link className="text-button auth-switch" to="/forgot-password">Forgot your password?</Link>}
  </section>
}

function PublicPage({ pageKey }) {
  const content = publicCopy[pageKey] || {
    title: titleFromKey(pageKey),
    description: 'BrandGuard helps teams review content consistently with approved brand guidance and human accountability.',
    bullets: ['Evidence-backed review', 'Shared workspaces', 'Auditable decisions'],
  }
  const isLanding = pageKey.endsWith('LandingPage')
  const isContact = pageKey.endsWith('ContactPage')
  if (isLanding) {
    return <div className="landing-page">
      <section className="landing-hero">
        <div className="landing-hero-copy">
          <span className="eyebrow">CONTENT REVIEW, WITH CLARITY</span>
          <h1>On brand.<br /><em>By design.</em></h1>
          <p>Bring your content, trusted guidance, and reviewers together in one calm, accountable workspace.</p>
          <div className="landing-actions">
            <Link className="button button-primary" to="/register">Build your workspace</Link>
            <Link className="button button-secondary" to="/how-it-works">See how it works</Link>
          </div>
        </div>
        <div className="product-preview" aria-label="Preview of the BrandGuard content review dashboard">
          <div className="preview-topbar"><span className="preview-brand-mark">B</span><strong>Brand workspace</strong><span className="preview-avatar">JD</span></div>
          <div className="preview-body">
            <div className="preview-heading"><div><small>MONDAY, OCTOBER 14</small><strong>Good morning, Jordan</strong></div><span className="preview-status">● All systems clear</span></div>
            <div className="preview-stats">
              <div><small>Content reviewed</small><strong>24</strong><span>↗ 12% this week</span></div>
              <div><small>Awaiting approval</small><strong>03</strong><span>Across 2 campaigns</span></div>
            </div>
            <div className="preview-reviews">
              <div className="preview-section-heading"><strong>Recent reviews</strong><span>View all&nbsp; →</span></div>
              <div className="preview-review-row"><span className="preview-file-icon">▤</span><span><strong>Autumn campaign</strong><small>Updated 12 minutes ago</small></span><span className="preview-pill">In review</span></div>
              <div className="preview-review-row"><span className="preview-file-icon">▤</span><span><strong>Product launch email</strong><small>Approved yesterday</small></span><span className="preview-pill preview-pill-approved">Approved</span></div>
            </div>
          </div>
        </div>
      </section>
      <section className="landing-feature">
        <div className="landing-feature-copy">
          <span className="eyebrow">PEOPLE IN CONTROL, AT EVERY STEP</span>
          <h2>Clear reviews.<br /><em>Confident teams.</em></h2>
          <Link className="button button-primary" to="/features">Explore the workflow</Link>
        </div>
      </section>
      <section className="landing-intro">
        <div className="intro-art">
          <div className="intro-card"><span className="intro-card-label">REVIEW PRINCIPLE</span><strong>Evidence first.<br />People decide.</strong><span className="intro-card-check">✓</span></div>
          <span className="intro-number">01 / 03</span>
        </div>
        <div className="intro-copy">
          <span className="eyebrow">FROM FIRST DRAFT TO FINAL SIGN-OFF</span>
          <h2>Make every review<br />a little more <span>certain.</span></h2>
          <p>Bring your content, brand guidance, and reviewers together. BrandGuard surfaces potential issues and supporting evidence—your team stays in control of every correction and approval.</p>
          <ul className="feature-list">
            <li><span>✓</span>Review findings alongside source evidence</li>
            <li><span>✓</span>Resolve comments and track approval decisions</li>
            <li><span>✓</span>Keep an audit trail from draft to sign-off</li>
          </ul>
          <Link className="text-button" to="/features">Explore the workflow <span aria-hidden="true">→</span></Link>
        </div>
      </section>
      <section className="landing-cta"><span className="eyebrow">READY WHEN YOUR TEAM IS</span><h2>Put your brand standards<br />to work.</h2><Link className="button button-primary" to="/register">Create an account</Link></section>
    </div>
  }
  return <div className={`marketing-page ${isLanding ? 'marketing-hero' : ''}`}>
    <span className="eyebrow">BRAND GOVERNANCE, MADE CLEAR</span>
    <h1>{content.title}</h1>
    <p className="marketing-description">{content.description}</p>
    {isContact
      ? <section className="content-card contact-card"><h2>Contact your workspace team</h2><p>For access, deployment, or data-retention questions, contact your organization’s BrandGuard administrator.</p><Link className="button button-primary" to="/login">Sign in to your workspace</Link></section>
      : <ul className="feature-list">{content.bullets.map((item) => <li key={item}><span aria-hidden="true">✓</span>{item}</li>)}</ul>}
    <div className="marketing-actions"><Link className="button button-primary" to="/register">Get started</Link><Link className="button button-secondary" to="/login">Sign in</Link></div>
  </div>
}

function UploadPanel({ onUpload, busy }) {
  return (
    <section id="upload-content" className="content-card">
      <div className="card-heading">
        <div>
          <h2>Upload content</h2>
          <p>Supported formats: PDF, DOCX, PPTX, PNG, JPG, WEBP, and TXT.</p>
        </div>
      </div>
      <FileUploader
        onFile={onUpload}
        busy={busy}
        accept={acceptedFileTypes}
      />
    </section>
  )
}

function SourceForm({ onSave, busy }) {
  const [error, setError] = useState('')
  async function submit(event) {
    event.preventDefault()
    const form = event.currentTarget
    const values = Object.fromEntries(new FormData(form).entries())
    try {
      setError('')
      await onSave(values)
      form.reset()
    } catch (saveError) {
      setError(saveError.message || 'Source could not be saved.')
    }
  }
  return <section className="content-card source-form-card">
    <h2>Add a source</h2><p>Sources should be approved and current before reviewers rely on them.</p>
    {error && <div className="notice notice-error" role="alert">{error}</div>}
    <form className="source-form" onSubmit={submit}>
      <label>Title<input name="title" minLength={2} maxLength={255} required /></label>
      <label>Type<select name="source_type"><option value="guideline">Brand guideline</option><option value="approved_claim">Approved claim</option><option value="terminology">Terminology</option><option value="reference">Reference</option></select></label>
      <label>Description<input name="description" maxLength={2000} /></label>
      <label>Source content<textarea name="content" maxLength={100000} rows={6} required /></label>
      <button className="button button-primary" disabled={busy}>{busy ? 'Saving…' : 'Save source'}</button>
    </form>
  </section>
}

function SettingsPanel({ pageKey }) {
  const storageKey = `brandguard_${pageKey.replaceAll('/', '_')}`
  const [saved, setSaved] = useState(false)
  const [enabled, setEnabled] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(storageKey) || '{"enabled":true}').enabled
    } catch {
      return true
    }
  })
  return <section className="content-card settings-card">
    <h2>{titleFromKey(pageKey)}</h2>
    <p>These preferences are stored only in this browser. Changes to your account, security credentials, or organization require API support.</p>
    <label className="toggle-setting"><input type="checkbox" checked={enabled} onChange={(event) => { setEnabled(event.target.checked); setSaved(false) }} /><span>Enable this preference on this device</span></label>
    <button className="button button-primary" onClick={() => { localStorage.setItem(storageKey, JSON.stringify({ enabled })); setSaved(true) }}>Save preference</button>
    {saved && <p className="notice notice-success" role="status">Preference saved on this device.</p>}
  </section>
}

function ProfileSettingsPanel({ pageKey }) {
  const { user, signOut } = useContext(AuthContext)
  const navigate = useNavigate()
  const [confirmSignOut, setConfirmSignOut] = useState(false)
  const [saved, setSaved] = useState(false)

  const storageKey = `brandguard_${pageKey.replaceAll('/', '_')}`

  const [enabled, setEnabled] = useState(() => {
    try {
      return JSON.parse(
        localStorage.getItem(storageKey) || '{"enabled":true}'
      ).enabled
    } catch {
      return true
    }
  })

  function savePreference() {
    localStorage.setItem(storageKey, JSON.stringify({ enabled }))
    setSaved(true)
  }

  function handleSignOut() {
    signOut()
    navigate('/login', { replace: true })
  }

  return (
    <div className="settings-page">

      <section className="content-card settings-card">
        <h2>Personal Information</h2>
        <p>Your account details and workspace identity.</p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '20px',
          marginTop: '20px'
        }}>
          <div>
            <small>Full Name</small>
            <h3>{user?.full_name || 'Not available'}</h3>
          </div>

          <div>
            <small>Email Address</small>
            <h3>{user?.email || 'Not available'}</h3>
          </div>

          <div>
            <small>Organization</small>
            <h3>{user?.organization_name || 'Not assigned'}</h3>
          </div>

          <div>
            <small>Account Role</small>
            <h3>{user?.role || user?.role_name || 'Not available'}</h3>
          </div>
        </div>

        <p style={{ marginTop: '18px' }}>
          These details are read from your signed-in account.
          Profile editing requires backend support.
        </p>
      </section>

      <section className="content-card settings-card">
        <h2>Preferences</h2>
        <p>Manage your local application preference.</p>

        <label className="toggle-setting">
          <input
            type="checkbox"
            checked={enabled}
            onChange={(event) => {
              setEnabled(event.target.checked)
              setSaved(false)
            }}
          />
          <span>Enable this preference on this device</span>
        </label>

        <button
          className="button button-primary"
          onClick={savePreference}
        >
          Save preference
        </button>

        {saved && (
          <p className="notice notice-success" role="status">
            Preference saved successfully.
          </p>
        )}
      </section>

      <section className="content-card settings-card">
        <h2>Security & Account</h2>
        <p>
          Manage your account security and access.
        </p>

        <div style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '12px',
          marginTop: '16px'
        }}>
          <Link
            to="/settings/security-settings"
            className="button button-secondary"
          >
            Security Settings
          </Link>

          <Link
            to="/settings/notification-settings"
            className="button button-secondary"
          >
            Notification Settings
          </Link>
        </div>
      </section>

      <section className="content-card settings-card">
        <h2>Sign Out</h2>
        <p>
          Sign out of your BrandGuard AI account on this device.
        </p>

        {!confirmSignOut ? (
          <button
            className="button button-primary"
            onClick={() => setConfirmSignOut(true)}
            style={{ background: '#b42318' }}
          >
            Sign Out
          </button>
        ) : (
          <div className="notice notice-warning" role="alert">
            <p>Are you sure you want to sign out?</p>

            <div style={{
              display: 'flex',
              gap: '12px',
              flexWrap: 'wrap'
            }}>
              <button
                className="button button-secondary"
                onClick={() => setConfirmSignOut(false)}
              >
                Cancel
              </button>

              <button
                className="button button-primary"
                onClick={handleSignOut}
                style={{ background: '#b42318' }}
              >
                Yes, Sign Out
              </button>
            </div>
          </div>
        )}
      </section>

    </div>
  )
}

function SecuritySettingsPanel() {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  async function handlePasswordChange(event) {
    event.preventDefault()

    setError('')
    setSuccess('')

    if (newPassword.length < 12) {
      setError('New password must contain at least 12 characters.')
      return
    }

    if (newPassword !== confirmPassword) {
      setError('The new passwords do not match.')
      return
    }

    if (currentPassword === newPassword) {
      setError('Your new password must be different from your current password.')
      return
    }

    setBusy(true)

    try {
      const result = await changePassword(
        currentPassword,
        newPassword
      )

      setSuccess(
        result?.message || 'Password changed successfully.'
      )

      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      setError(
        err?.response?.data?.detail ||
        err?.message ||
        'Unable to change your password. Please try again.'
      )
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="settings-page">

      {/* Account Security */}
      <section className="content-card settings-card">
        <h2>Account Security</h2>

        <p>
          Protect your BrandGuard AI account and manage your
          authentication credentials.
        </p>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
            gap: '16px',
            marginTop: '20px'
          }}
        >
          <div>
            <small>Authentication</small>
            <h3>Account protected</h3>
            <p>Authenticated access is required.</p>
          </div>

          <div>
            <small>Password Management</small>
            <h3>Password controls</h3>
            <p>Update your account password securely.</p>
          </div>
        </div>
      </section>

      {/* Change Password */}
      <section className="content-card settings-card">
        <div className="card-heading">
          <div>
            <h2>Change Password</h2>
            <p>
              Enter your current password and choose a new password.
            </p>
          </div>
        </div>

        {error && (
          <div className="notice notice-error" role="alert">
            {error}
          </div>
        )}

        {success && (
          <div className="notice notice-success" role="status">
            {success}
          </div>
        )}

        <form
          className="auth-form"
          onSubmit={handlePasswordChange}
        >
          <label>
            Current Password

            <input
              type="password"
              value={currentPassword}
              onChange={(event) =>
                setCurrentPassword(event.target.value)
              }
              autoComplete="current-password"
              placeholder="Enter current password"
              required
            />
          </label>

          <label>
            New Password

            <input
              type="password"
              value={newPassword}
              onChange={(event) =>
                setNewPassword(event.target.value)
              }
              autoComplete="new-password"
              placeholder="Enter new password"
              minLength={12}
              maxLength={128}
              required
            />
          </label>

          <label>
            Confirm New Password

            <input
              type="password"
              value={confirmPassword}
              onChange={(event) =>
                setConfirmPassword(event.target.value)
              }
              autoComplete="new-password"
              placeholder="Confirm new password"
              minLength={12}
              maxLength={128}
              required
            />
          </label>

          <p>
            Password requirements: minimum 12 characters.
          </p>

          <button
            type="submit"
            className="button button-primary"
            disabled={busy}
          >
            {busy ? 'Updating Password...' : 'Update Password'}
          </button>
        </form>
      </section>

    </div>
  )
}


function NotificationSettingsPanel() {
  const [preferences, setPreferences] = useState({
    in_app_enabled: true,
    email_enabled: false,
    security_alerts_enabled: true,
    document_updates_enabled: true,
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    let active = true

    async function loadPreferences() {
      try {
        const result = await getNotificationPreferences()
        if (active) setPreferences(result)
      } catch (err) {
        if (active) setError(err.message || 'Unable to load preferences.')
      } finally {
        if (active) setLoading(false)
      }
    }

    loadPreferences()
    return () => { active = false }
  }, [])

  async function handleSave(event) {
    event.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const result = await saveNotificationPreferences(preferences)
      setPreferences(result.preferences || preferences)
      setSuccess(result.message || 'Preferences saved successfully.')
    } catch (err) {
      setError(err.message || 'Unable to save preferences.')
    } finally {
      setSaving(false)
    }
  }

  const options = [
    ['in_app_enabled', 'In-app notifications', 'Receive alerts inside your workspace.'],
    ['email_enabled', 'Email notifications', 'Save your preference for future email delivery.'],
    ['security_alerts_enabled', 'Security alerts', 'Important account and password activity.'],
    ['document_updates_enabled', 'Document and review updates', 'Upload, processing, review, and approval updates.'],
  ]

  if (loading) {
    return <section className="content-card settings-card"><p>Loading notification preferences...</p></section>
  }

  return (
    <div className="settings-page">
      <section className="content-card settings-card">
        <h2>Notification Preferences</h2>
        <p>Choose which updates you want to receive. Your preferences are saved to your account.</p>

        {error && <div className="notice notice-error" role="alert">{error}</div>}
        {success && <div className="notice notice-success" role="status">{success}</div>}

        <form onSubmit={handleSave}>
          <div style={{ display: 'grid', gap: '16px', marginTop: '20px' }}>
            {options.map(([key, title, description]) => (
              <label key={key} style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '16px',
                padding: '16px',
                border: '1px solid var(--border-color, #ddd)',
                borderRadius: '12px',
                cursor: 'pointer',
              }}>
                <span>
                  <strong style={{ display: 'block', marginBottom: '5px' }}>{title}</strong>
                  <small>{description}</small>
                </span>
                <input
                  type="checkbox"
                  checked={Boolean(preferences[key])}
                  onChange={(event) => {
                    setPreferences((current) => ({
                      ...current,
                      [key]: event.target.checked,
                    }))
                    setSuccess('')
                  }}
                  style={{ width: '20px', height: '20px', flexShrink: 0 }}
                />
              </label>
            ))}
          </div>

          <button type="submit" className="button button-primary" disabled={saving} style={{ marginTop: '24px' }}>
            {saving ? 'Saving...' : 'Save Preferences'}
          </button>
        </form>
      </section>
    </div>
  )
}

export default function PageView({ pageKey }) {
  const group = getGroup(pageKey)
  const title = titleFromKey(pageKey)
  const params = useParams()
  const navigate = useNavigate()
  const { activeWorkspace } = useContext(WorkspaceContext)
  const { addNotification, notifications, markAllRead } = useContext(NotificationContext)
  const [data, setData] = useState(null)
  const [comments, setComments] = useState([])
  const [loading, setLoading] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [query, setQuery] = useState('')
  const entityId = params.id || params.documentId || params.reviewId
  const reload = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const result = await loadPageData(pageKey, entityId)
      setData(result)
      if (group === 'review' && (pageKey.includes('ReviewDetails') || pageKey.includes('ReviewComments')) && result?.id) {
        setComments(await listComments(result.id))
      } else {
        setComments([])
      }
    } catch (requestError) {
      setError(requestError.message || 'Workspace data could not be loaded.')
    } finally {
      setLoading(false)
    }
  }, [pageKey, entityId, group])

  useEffect(() => {
    if (group === 'public' || group === 'auth' || group === 'errors' || group === 'settings' || group === 'admin' || group === 'publishing') {
      setData(null)
      return
    }
    if (group === 'dashboard' && pageKey.endsWith('NotificationsPage')) return
    reload()
  }, [group, pageKey, reload])

  useEffect(() => {
    if (group === 'dashboard' && pageKey.endsWith('NotificationsPage')) setData(notifications)
  }, [group, pageKey, notifications])

  const rows = useMemo(() => rowsFrom(data).filter((row) => {
    const haystack = [row.title, row.document_title, row.original_filename, row.description, row.status, row.source_type]
      .filter(Boolean).join(' ').toLowerCase()
    return haystack.includes(query.toLowerCase())
  }), [data, query])

  async function handleUpload(file) {
    console.log('[BrandGuard] handleUpload triggered:', file?.name, file?.size)
    const validationError = validateUploadFile(file)
    if (validationError) {
      setError(validationError)
      throw new Error(validationError)
    }
    setBusy(true)
    setError('')
    try {
      const document = await uploadDocument(file, activeWorkspace?.id)
      addNotification({ title: 'Upload complete', message: `${file.name} is ready for review.`, href: `/documents/${document.id}` })
      navigate(`/documents/${document.id}`)
    } catch (requestError) {
      setError(requestError.message || 'Upload failed.')
      throw requestError
    } finally {
      setBusy(false)
    }
  }

  async function handleRunReview(document) {
    setBusy(true)
    setError('')
    try {
      const review = await runReview(document.id)
      addNotification({ title: 'Review complete', message: `${document.title || document.original_filename} has a completed review.`, href: `/reviews/${review.id}` })
      navigate(`/reviews/${review.id}`)
    } catch (requestError) {
      setError(requestError.message || 'Review could not be run.')
    } finally {
      setBusy(false)
    }
  }

  async function handleSourceSave(values) {
    setBusy(true)
    try {
      await createSource({ ...values, description: values.description || null })
      addNotification({ title: 'Source created', message: 'The source needs verification before it can be used as evidence.' })
      await reload()
    } finally {
      setBusy(false)
    }
  }

  async function handleApproveSource(sourceId, versionId) {
    setBusy(true)
    setError('')
    try {
      await approveSourceVersion(sourceId, versionId)
      addNotification({ title: 'Source verified', message: 'The source version is now approved for review use.' })
      await reload()
    } catch (requestError) {
      setError(requestError.message || 'The source version could not be verified.')
    } finally {
      setBusy(false)
    }
  }

  async function handleApprovalDecision(approval, decision) {
    let note = ''
    if (decision === 'rejected') {
      note = window.prompt('What changes are required?') || ''
      if (!note.trim()) return
    }
    setBusy(true)
    setError('')
    try {
      await decideApproval(approval.id, decision, note)
      addNotification({ title: 'Approval updated', message: decision === 'approved' ? 'Approval was recorded.' : 'Changes were requested.' })
      await reload()
    } catch (requestError) {
      setError(requestError.message || 'The approval could not be updated.')
    } finally {
      setBusy(false)
    }
  }

  async function handleFindingDecision(finding, decision) {
    setBusy(true)
    setError('')
    try {
      await decideFinding(finding.id, decision)
      await reload()
    } catch (requestError) {
      setError(requestError.message || 'The finding could not be updated.')
    } finally {
      setBusy(false)
    }
  }

  async function handleComment(body) {
    if (!data?.id) return
    setBusy(true)
    try {
      await addComment(data.id, body)
      setComments(await listComments(data.id))
    } catch (requestError) {
      setError(requestError.message || 'Comment could not be posted.')
    } finally {
      setBusy(false)
    }
  }

  async function handleRequestApproval() {
    setBusy(true)
    try {
      await requestApproval(data.id)
      addNotification({ title: 'Approval requested', message: 'The review was submitted for human approval.' })
      navigate('/approvals')
    } catch (requestError) {
      setError(requestError.message || 'Approval could not be requested.')
    } finally {
      setBusy(false)
    }
  }

  if (group === 'auth') return <AuthPage pageKey={pageKey} />
  if (group === 'public') return <PublicPage pageKey={pageKey} />
  if (group === 'errors') {
    const isMaintenance = pageKey.endsWith('MaintenancePage')
    const isServerError = pageKey.endsWith('ServerErrorPage')
    const isUnauthorized = pageKey.endsWith('UnauthorizedPage')
    const heading = isMaintenance ? 'We’ll be back soon' : isServerError ? 'Something went wrong' : isUnauthorized ? 'Access denied' : 'Page not found'
    const text = isMaintenance ? 'BrandGuard is temporarily unavailable for maintenance.'
      : isServerError ? 'The request could not be completed. Please try again or contact your workspace administrator.'
        : isUnauthorized ? 'Your account does not have permission to access this page.'
          : 'The page may have moved or the link may be incorrect.'
    return <EmptyState title={heading} text={text} action={<Link className="button button-primary" to="/dashboard">Go to workspace</Link>} />
  }
  
if (group === 'settings') {
  return (
    <>
      <PageHeader title={title} description={resourceMessages.settings} />

      {pageKey.endsWith('ProfileSettingsPage') ? (
        <ProfileSettingsPanel pageKey={pageKey} />
      ) : pageKey.endsWith('SecuritySettingsPage') ? (
        <SecuritySettingsPanel />
      ) : pageKey.endsWith('NotificationSettingsPage') ? (
        <NotificationSettingsPanel />
      ) : (
        <SettingsPanel pageKey={pageKey} />
      )
    }
    </>
  )
}

  if (group === 'admin') return <><PageHeader title={title} description={getDescription(group, title)} /><div className="notice notice-warning">{resourceMessages.admin}</div><SettingsPanel pageKey={pageKey} /></>
  if (group === 'publishing') return <><PageHeader title={title} description={getDescription(group, title)} /><div className="notice notice-warning">{resourceMessages.publishing}</div><EmptyState title="No publishing items are available" text="The application will show release packages here after the publishing API is enabled." /></>

  if (loading && data === null) return <LoadingSpinner label={`Loading ${title.toLowerCase()}`} />
  const isDashboard = group === 'dashboard' && !pageKey.endsWith('NotificationsPage')
  const isAnalytics = group === 'analytics'
  const detail = data && !Array.isArray(data) && typeof data === 'object' && data.id
  const description = getDescription(group, title)
  const showUpload = group === 'documents' && (pageKey.includes('UploadDocument') || pageKey.includes('AllDocuments'))
  const showSourceForm = group === 'sources' && (pageKey.includes('AddSource') || pageKey.includes('SourceRegister'))

  if (error && !data) return <><PageHeader title={title} description={description} /><div className="notice notice-error" role="alert">{error}<button className="text-button" onClick={reload}>Retry</button></div></>

  if (isDashboard && data) {
    const documents = data.documents || []
    const reviews = data.reviews || []
    const approvals = data.approvals || []
    const pending = approvals.filter((item) => item.status === 'pending').length
    const findings = reviews.reduce((count, item) => count + (item.findings || []).filter((finding) => finding.status === 'open').length, 0)
    return <>
      <PageHeader title={title} description={description} action={<Link className="button button-primary" to="/documents/upload">+ New review</Link>} />
      {error && <div className="notice notice-error" role="alert">{error}</div>}
      <div className="summary-grid"><StatCard label="Documents" value={documents.length} detail="In this workspace" /><StatCard label="Reviews" value={reviews.length} detail="Completed and in progress" /><StatCard label="Open findings" value={findings} detail="Across available reviews" /><StatCard label="Pending approvals" value={pending} detail="Awaiting a decision" /></div>
      <section id="upload-content"className="content-card"><header className="card-heading"><div><h2>Recent documents</h2><p>Content recently added to your workspace</p></div><Link className="text-button" to="/documents">All documents →</Link></header><DataTable rows={documents.slice(0, 5)} group="documents" onRunReview={handleRunReview} busy={busy} /></section>
      <section  id="upload-content"className="content-card"><header className="card-heading"><div><h2>Review activity</h2><p>Recent reviews recorded by the API</p></div></header><ActivityChart data={Object.entries(documents.reduce((counts, item) => { counts[formatStatus(item.status)] = (counts[formatStatus(item.status)] || 0) + 1; return counts }, {})).map(([label, value]) => ({ label, value }))} /></section>
    </>
  }

  if (isAnalytics && data) {
    return <>
      <PageHeader title={title} description={resourceMessages.analytics} />
      <div className="summary-grid"><StatCard label="Documents" value={data.documents} /><StatCard label="Reviews" value={data.reviews} /><StatCard label="Pending approvals" value={data.approvalsPending} /><StatCard label="Open findings" value={data.openFindings} /></div>
      <section id="upload-content" className="content-card"><h2>Documents by status</h2><ActivityChart data={Object.entries(data.documentsByStatus || {}).map(([label, value]) => ({ label: formatStatus(label), value }))} /></section>
      <section id="upload-content" className="content-card"><h2>Recent reviews</h2><DataTable rows={data.recentReviews || []} group="review" busy={busy} /></section>
    </>
  }

  if (group === 'dashboard' && pageKey.endsWith('NotificationsPage')) {
    return <><PageHeader title={title} description="Updates generated by actions in this browser." action={<button className="button button-secondary" onClick={markAllRead}>Mark all read</button>} /><section className="content-card">{notifications.length ? notifications.map((item) => <article className="notification-item" key={item.id}><div><strong>{item.title}</strong><p>{item.message}</p><small>{formatDateTime(item.created_at)}</small></div><span>{item.read ? 'Read' : 'Unread'}</span></article>) : <EmptyState title="No notifications" text="Workspace updates will appear here." />}</section></>
  }

  if (group === 'review' && detail) {
    const unresolved = (data.findings || []).filter((finding) => finding.status === 'open')
    return <>
      <PageHeader title={data.document_title || `${title} #${String(data.id).slice(0, 8)}`} description={`${formatStatus(data.status)} · ${(data.findings || []).length} finding(s)`} action={<button className="button button-primary" disabled={busy || unresolved.length > 0} onClick={handleRequestApproval}>{unresolved.length ? `Resolve ${unresolved.length} finding(s)` : 'Request approval'}</button>} />
      {error && <div className="notice notice-error" role="alert">{error}</div>}
      <ReviewWorkspace review={data} comments={comments} onComment={handleComment} onDecision={handleFindingDecision} busy={busy} />

    </>
  }

  if (group === 'documents' && detail) {
    return <>
      <PageHeader title={data.title || data.original_filename} description={`${formatStatus(data.status)} · Updated ${formatDateTime(data.updated_at)}`} action={<button className="button button-primary" disabled={busy} onClick={() => handleRunReview(data)}>Run review</button>} />
      {error && <div className="notice notice-error" role="alert">{error}</div>}
      <div className="details-grid"><section className="content-card"><h2>Document details</h2><DocumentMetadata document={data} /></section><section className="content-card"><h2>Review status</h2><p><DocumentStatusBadge status={data.latest_review_status || data.status} /></p>{data.latest_review_id && <Link className="button button-secondary" to={`/reviews/${data.latest_review_id}`}>Open latest review</Link>}<p className="muted">Review findings and approval decisions are stored separately from the original upload.</p></section></div>
    </>
  }

  if (group === 'sources' && detail) {
    return <>
      <PageHeader title={data.title} description={data.description || formatStatus(data.source_type || 'reference')} />
      {error && <div className="notice notice-error" role="alert">{error}</div>}
      <section className="content-card">
        <header className="card-heading"><div><h2>Source versions</h2><p>Only approved versions can be used as evidence in a review.</p></div><DocumentStatusBadge status={data.status} /></header>
        {(data.versions || []).length
          ? <div className="source-list">{data.versions.map((version) => <article className="source-item" key={version.id}><div><h3>Version {version.version_number || version.version || '—'}</h3><p>{version.description || version.content || 'Source version'}</p><small>{formatDateTime(version.created_at)}</small></div><DocumentStatusBadge status={version.status} />{version.status !== 'approved' && <button className="button button-secondary" disabled={busy} onClick={() => handleApproveSource(data.id, version.id)}>Verify version</button>}</article>)}</div>
          : <EmptyState title="No versions available" text="Add a version before this source can be verified." />}
      </section>
    </>
  }

  let visibleRows = detail ? [data] : rows
  if (pageKey.includes('ArchivedDocuments')) visibleRows = visibleRows.filter((item) => item.status === 'archived')
  if (pageKey.includes('ChangesRequested')) visibleRows = visibleRows.filter((item) => item.status === 'dismissed')
  if (pageKey.includes('ClaimsRegister')) visibleRows = visibleRows.filter((item) => item.source_type === 'approved_claim')
  if (pageKey.includes('Terminology')) visibleRows = visibleRows.filter((item) => item.source_type === 'terminology')
  if (pageKey.includes('FactSheets')) visibleRows = visibleRows.filter((item) => item.source_type === 'fact_sheet')
  return <>
   <PageHeader
  title={title}
  description={description}
  action={
    showUpload ? (
      <a
        className="button button-primary"
        href="#upload-content"
      >
        + Upload content
      </a>
    ) : undefined
  }
/>
    {error && <div className="notice notice-error" role="alert">{error}<button className="text-button" onClick={reload}>Retry</button></div>}
    {showUpload && <UploadPanel onUpload={handleUpload} busy={busy} />}
    {showSourceForm && <SourceForm onSave={handleSourceSave} busy={busy} />}
    {group !== 'settings' && group !== 'admin' && <section className="content-card">
      <header className="card-heading"><div><h2>{group === 'documents' ? 'Document library' : group === 'approvals' ? 'Approval requests' : group === 'sources' ? 'Source register' : group === 'workspace' ? 'Workspace members' : title}</h2><p>{visibleRows.length} item(s) available</p></div><label className="table-search"><span className="sr-only">Search</span><input type="search" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search…" /></label></header>
      {loading && <LoadingSpinner label="Refreshing data" />}
      {group === 'approvals'
        ? <DataTable rows={visibleRows} group={group} onApprovalDecision={handleApprovalDecision} busy={busy} />
        : group === 'documents'
          ? <DataTable rows={visibleRows} group={group} onRunReview={handleRunReview} busy={busy} />
          : <DataTable rows={visibleRows} group={group} busy={busy} />}
    </section>}
    {group === 'review' && !detail && <div className="notice notice-info">Select a review to inspect its findings and supporting evidence.</div>}
    {group === 'sources' && visibleRows.some((source) => source.versions?.some((version) => version.status !== 'approved')) && <div className="notice notice-info">New source versions must be verified before they can support review findings.</div>}
    {group === 'publishing' && <p className="muted">{resourceMessages.publishing}</p>}
  </>
}


