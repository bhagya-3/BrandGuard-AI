import { useCallback, useEffect, useState } from 'react'

export default function useAsync(operation, dependencies = []) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadVersion, setReloadVersion] = useState(0)

  const reload = useCallback(() => setReloadVersion((version) => version + 1), [])

  useEffect(() => {
    let active = true
    setLoading(true)
    setError('')
    Promise.resolve()
      .then(operation)
      .then((result) => {
        if (active) setData(result)
      })
      .catch((requestError) => {
        if (active) setError(requestError.message || 'The request could not be completed.')
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => { active = false }
  // operation is intentionally supplied with its inputs in dependencies.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...dependencies, reloadVersion])

  return { data, setData, loading, error, setError, reload }
}
