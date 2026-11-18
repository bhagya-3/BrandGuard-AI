const ROLE_LEVEL = {
  viewer: 1,
  member: 2,
  reviewer: 3,
  approver: 4,
  admin: 5,
  owner: 6,
}

export function getUserRole(user) {
  return String(user?.role || user?.role_name || 'member').toLowerCase()
}

export function hasRole(user, roles = []) {
  if (!Array.isArray(roles) || roles.length === 0) return Boolean(user)
  const role = getUserRole(user)
  return roles.map((item) => String(item).toLowerCase()).includes(role)
}

export function hasMinimumRole(user, minimumRole) {
  const userLevel = ROLE_LEVEL[getUserRole(user)] || 0
  const requiredLevel = ROLE_LEVEL[String(minimumRole).toLowerCase()] || Infinity
  return userLevel >= requiredLevel
}

export function canManageWorkspace(user) {
  return hasMinimumRole(user, 'admin')
}

export function canReview(user) {
  return hasMinimumRole(user, 'reviewer')
}