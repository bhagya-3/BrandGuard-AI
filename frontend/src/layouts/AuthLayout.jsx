import { Link, Outlet } from 'react-router-dom'
import { BrandLogo } from '../components/shared.jsx'

export default function AuthLayout() {
  return (
    <main className="auth-layout">
      <header className="auth-layout-header"><BrandLogo /><Link to="/">Back to home</Link></header>
      <div className="auth-layout-content"><Outlet /></div>
      <footer className="auth-layout-footer">Secure, organization-scoped content review.</footer>
    </main>
  )
}