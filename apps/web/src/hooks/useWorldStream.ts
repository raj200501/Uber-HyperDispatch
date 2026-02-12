import { useEffect } from 'react'
import { buildMockSnapshot } from '../types'
import { useWorld } from '../store/world-store'

export function useWorldStream() {
  const { dispatch } = useWorld()
  useEffect(() => {
    let tick = 0
    dispatch({ type: 'conn', payload: true })
    const timer = setInterval(() => {
      tick += 1
      dispatch({ type: 'snapshot', payload: buildMockSnapshot(Date.now() + tick * 200) })
    }, 200)
    return () => {
      clearInterval(timer)
      dispatch({ type: 'conn', payload: false })
    }
  }, [dispatch])
}
