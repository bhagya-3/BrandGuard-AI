import { useCallback, useState } from 'react'
import {
  addComment,
  decideFinding,
  getReview,
  listComments,
  runReview,
} from '../services/reviewService.js'

export default function useReview() {
  const [review, setReview] = useState(null)
  const [comments, setComments] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const run = useCallback(async (documentId) => {
    setLoading(true)
    setError('')
    try {
      const result = await runReview(documentId)
      setReview(result)
      return result
    } catch (requestError) {
      setError(requestError.message || 'Review could not be run.')
      throw requestError
    } finally {
      setLoading(false)
    }
  }, [])

  const load = useCallback(async (reviewId) => {
    setLoading(true)
    setError('')
    try {
      const [result, nextComments] = await Promise.all([
        getReview(reviewId),
        listComments(reviewId),
      ])
      setReview(result)
      setComments(nextComments)
      return result
    } catch (requestError) {
      setError(requestError.message || 'Review could not be loaded.')
      throw requestError
    } finally {
      setLoading(false)
    }
  }, [])

  const decide = useCallback(async (findingId, decision, suggestedText) => {
    await decideFinding(findingId, decision, suggestedText)
    if (review?.id) await load(review.id)
  }, [review?.id, load])

  const comment = useCallback(async (body, findingId) => {
    if (!review?.id) throw new Error('Open a review before adding a comment.')
    const created = await addComment(review.id, body, findingId)
    setComments((current) => [...current, created])
    return created
  }, [review?.id])

  return { review, comments, loading, error, run, load, decide, comment, setReview }
}