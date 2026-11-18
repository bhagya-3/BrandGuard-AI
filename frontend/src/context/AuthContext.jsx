import { createContext, useCallback, useEffect, useMemo, useState } from 'react'
import {
  getCurrentUser,
  login as authenticate,
  logout as clearSession,
  register as createAccount,
} from '../services/authService.js'
import { getAccessToken, setAccessToken } from '../services/apiClient.js'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(getAccessToken()))
  const [error, setError] = useState('')

  const refreshUser = useCallback(async () => {
    if (!getAccessToken()) {
      setUser(null)
      setLoading(false)
      return null
    }
    setLoading(true)
    try {
      const currentUser = await getCurrentUser()
      setUser(currentUser)
      setError('')
      return currentUser
    } catch (requestError) {
      setAccessToken(null)
      setUser(null)
      setError(requestError.message || 'Your session could not be restored.')
      throw requestError
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!getAccessToken()) {
      setLoading(false)
      return
    }
    refreshUser().catch(() => {})
  }, [refreshUser])

  const signIn = useCallback(async (credentials) => {
    setLoading(true)
    setError('')
    try {
      const member = await authenticate(credentials)
      setUser(member)
      return member
    } catch (requestError) {
      setError(requestError.message || 'Sign-in failed.')
      throw requestError
    } finally {
      setLoading(false)
    }
  }, [])

  const signUp = useCallback(async (details) => {
    setLoading(true)
    setError('')
    try {
      const member = await createAccount(details)
      setUser(member)
      return member
    } catch (requestError) {
      setError(requestError.message || 'Account creation failed.')
      throw requestError
    } finally {
      setLoading(false)
    }
  }, [])

  const signOut = useCallback(() => {
    clearSession()
    setUser(null)
    setError('')
  }, [])

  const value = useMemo(() => ({
    user,
    loading,
    error,
    isAuthenticated: Boolean(user),
    signIn,
    signUp,
    signOut,
    refreshUser,
    clearError: () => setError(''),
  }), [user, loading, error, signIn, signUp, signOut, refreshUser])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}