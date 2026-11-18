import { useMemo } from 'react'
import useAuth from './useAuth.js'
import { canManageWorkspace, canReview, hasMinimumRole, hasRole } from '../utils/permissions.js'

export default function usePermissions() {
  const { user } = useAuth()
  return useMemo(() => ({
    role: user?.role || user?.role_name || 'member',
    hasRole: (roles) => hasRole(user, roles),
    hasMinimumRole: (role) => hasMinimumRole(user, role),
    canManageWorkspace: canManageWorkspace(user),
    canReview: canReview(user),
  }), [user])
}