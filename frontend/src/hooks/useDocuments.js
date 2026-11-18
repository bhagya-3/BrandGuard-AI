import { useCallback } from 'react'
import { listDocuments, uploadDocument } from '../services/documentService.js'
import useAsync from './useAsync.js'

export default function useDocuments(workspaceId) {
  const load = useCallback(() => listDocuments(), [])
  const resource = useAsync(load, [])

  const upload = useCallback(async (file) => {
    const created = await uploadDocument(file, workspaceId)
    resource.setData((current) => [created, ...(Array.isArray(current) ? current : [])])
    return created
  }, [workspaceId, resource.setData])

  return {
    documents: Array.isArray(resource.data) ? resource.data : [],
    loading: resource.loading,
    error: resource.error,
    upload,
    refresh: resource.reload,
  }
}