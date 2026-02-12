import { useEffect } from 'react'
import { useWorld } from '../store/world-store'

export function useTraceStream() {
  const { dispatch } = useWorld()
  useEffect(() => {
    let count = 0
    const timer = setInterval(() => {
      count += 1
      dispatch({
        type: 'trace',
        payload: {
          trace_id: `trace-${count % 12}`,
          span_id: `span-${count}`,
          parent_span_id: undefined,
          name: ['validate', 'fetch', 'filter', 'score', 'claim'][count % 5],
          start_ns: Date.now() * 1_000_000,
          end_ns: Date.now() * 1_000_000 + 10_000_000,
          tags: { candidate_count: count % 9 },
          logs: ['ok'],
        },
      })
    }, 500)
    return () => clearInterval(timer)
  }, [dispatch])
}
