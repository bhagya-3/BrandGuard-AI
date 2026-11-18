import { Outlet } from 'react-router-dom'
import { Footer, Navbar } from '../components/shared.jsx'

export default function PublicLayout() {
  return <div className="public-shell"><Navbar /><main className="public-content"><Outlet /></main><Footer /></div>
}