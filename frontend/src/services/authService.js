import { apiPost, apiRequest, setAccessToken } from './apiClient.js'

export async function login(credentials) {
  const result = await apiPost('/auth/login', credentials)
  if (!result?.access_token || !result?.user) {
    throw new Error('The server returned an incomplete sign-in response.')
  }
  setAccessToken(result.access_token)
  return result.user
}

export async function register(details) {
  const result = await apiPost('/auth/register', details)
  if (!result?.access_token || !result?.user) {
    throw new Error('The server returned an incomplete registration response.')
  }
  setAccessToken(result.access_token)
  return result.user
}

export async function getCurrentUser() {
  return apiRequest('/auth/me')
}

export function logout() {
  setAccessToken(null)
}

export async function requestPasswordReset(email) {
  return apiPost('/auth/forgot-password', { email })
}

export async function resetPassword(token, password) {
  return apiPost('/auth/reset-password', { token, password })
}

export async function verifyEmail(token) {
  return apiPost('/auth/verify-email', { token })
}
export async function changePassword(currentPassword, newPassword) {
  return apiPost('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  })
}