import { useEffect } from 'react'
import { useWorld } from '../store/world-store'

export function useWorldWS() {
  const { dispatch } = useWorld()
  useEffect(() => {
    let stop = false
    let retry = 1000
    let ws: WebSocket | null = null
    const connect = () => {
      ws = new WebSocket('ws://127.0.0.1:8000/ws/world')
      ws.onopen = () => dispatch({ type: 'conn', payload: true })
      ws.onmessage = (ev) => dispatch({ type: 'snapshot', payload: JSON.parse(ev.data) })
      ws.onclose = () => {
        dispatch({ type: 'conn', payload: false })
        if (!stop) setTimeout(connect, retry)
      }
    }
    connect()
    return () => {
      stop = true
      ws?.close()
    }
  }, [dispatch])
}
