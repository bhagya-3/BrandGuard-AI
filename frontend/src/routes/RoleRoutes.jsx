import { Navigate, Outlet } from 'react-router-dom'
import useAuth from '../hooks/useAuth.js'
import { LoadingSpinner } from '../components/shared.jsx'
import { hasMinimumRole } from '../utils/permissions.js'

export default function RoleRoutes({ minimumRole = null }) {
  const { user, loading, isAuthenticated } = useAuth()
  if (loading) return <LoadingSpinner fullScreen label="Checking access" />
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (minimumRole && !hasMinimumRole(user, minimumRole)) return <Navigate to="/unauthorized" replace />
  return <Outlet />
}