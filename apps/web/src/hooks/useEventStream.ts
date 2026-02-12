import { useEffect } from 'react'
import { useWorld } from '../store/world-store'

export function useEventStream() {
  const { dispatch } = useWorld()
  useEffect(() => {
    const events = new Array(30).fill(null).map((_, i) => ({
      ts: Date.now() - i * 900,
      type: i % 7 === 0 ? 'ANOMALY' : 'MATCHED',
      city_id: 'sf',
      payload: { request_id: `req-${i}`, driver_id: `d-${i % 10}` },
    }))
    dispatch({ type: 'events', payload: events })
  }, [dispatch])
}
