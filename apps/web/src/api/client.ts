import type { DispatchEvent, WorldSnapshot } from './types'

const BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8000'

async function parse<T>(resp: Response): Promise<T> {
  if (!resp.ok) {
    const text = await resp.text()
    throw new Error(`HTTP ${resp.status}: ${text || 'request failed'}`)
  }
  return (await resp.json()) as T
}

export const apiClient = {
  async healthz(): Promise<{ ok: boolean }> {
    const resp = await fetch(`${BASE}/healthz`)
    return parse<{ ok: boolean }>(resp)
  },
  async world(): Promise<WorldSnapshot> {
    const resp = await fetch(`${BASE}/world`)
    return parse<WorldSnapshot>(resp)
  },
  async events(fromTs = 0): Promise<DispatchEvent[]> {
    const resp = await fetch(`${BASE}/replay/events?from_ts=${fromTs}`)
    return parse<DispatchEvent[]>(resp)
  },
}
