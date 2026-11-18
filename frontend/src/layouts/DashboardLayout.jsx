import { Link, Outlet } from 'react-router-dom'
import { NotificationBell, Sidebar } from '../components/shared.jsx'
import useAuth from '../hooks/useAuth.js'
import { initials } from '../utils/formatters.js'

export default function DashboardLayout({ admin = false }) {
  const { user } = useAuth()
  return (
    <div className="workspace-shell">
      <Sidebar admin={admin} />
      <main className="workspace-main">
        <header className="workspace-topbar">
          <div className="topbar-identity"><span className="live-status" /> Signed in as <strong>{user?.full_name || user?.email}</strong></div>
          <div className="topbar-actions"><span className="topbar-protection">Protected workspace</span><NotificationBell /><Link to="/settings/profile-settings" className="user-avatar" aria-label="Profile settings">{initials(user?.full_name || user?.email)}</Link></div>
        </header>
        <div className="workspace-content"><Outlet /></div>
        <footer className="workspace-footer"><span>BrandGuard AI</span><span>Creator → review engine → human approval → audit trail</span></footer>
      </main>
    </div>
  )
}