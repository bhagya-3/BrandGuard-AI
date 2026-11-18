import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { apiRequest } from '../services/apiClient.js'
import { AuthContext } from './AuthContext.jsx'

const STORAGE_KEY = 'brandguard_active_workspace'
export const WorkspaceContext = createContext(null)

export function WorkspaceProvider({ children }) {
  const { user, isAuthenticated } = useContext(AuthContext)
  const [workspaces, setWorkspaces] = useState([])
  const [activeWorkspace, setActiveWorkspace] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const refreshWorkspaces = useCallback(async () => {
    if (!isAuthenticated) {
      setWorkspaces([])
      setActiveWorkspace(null)
      return []
    }
    setLoading(true)
    setError('')
    try {
      const result = await apiRequest('/workspaces/')
      if (!Array.isArray(result)) throw new Error('The server returned an invalid workspace list.')
      setWorkspaces(result)
      const savedId = typeof window === 'undefined' ? null : window.localStorage.getItem(STORAGE_KEY)
      const selected = result.find((item) => item.id === savedId)
        || result.find((item) => item.id === user?.workspace_id)
        || result[0]
        || null
      setActiveWorkspace(selected)
      if (typeof window !== 'undefined') {
        if (selected?.id) window.localStorage.setItem(STORAGE_KEY, selected.id)
        else window.localStorage.removeItem(STORAGE_KEY)
      }
      return result
    } catch (requestError) {
      setError(requestError.message || 'Workspaces could not be loaded.')
      throw requestError
    } finally {
      setLoading(false)
    }
  }, [isAuthenticated, user?.workspace_id])

  useEffect(() => {
    if (!isAuthenticated) {
      setWorkspaces([])
      setActiveWorkspace(null)
      setError('')
      return
    }
    refreshWorkspaces().catch(() => {})
  }, [isAuthenticated, refreshWorkspaces])

  const selectWorkspace = useCallback((workspaceId) => {
    const workspace = workspaces.find((item) => item.id === workspaceId)
    if (!workspace) throw new Error('That workspace is not available to your account.')
    setActiveWorkspace(workspace)
    if (typeof window !== 'undefined') window.localStorage.setItem(STORAGE_KEY, workspace.id)
  }, [workspaces])

  const value = useMemo(() => ({
    workspaces,
    activeWorkspace,
    loading,
    error,
    selectWorkspace,
    refreshWorkspaces,
  }), [workspaces, activeWorkspace, loading, error, selectWorkspace, refreshWorkspaces])

  return <WorkspaceContext.Provider value={value}>{children}</WorkspaceContext.Provider>
}