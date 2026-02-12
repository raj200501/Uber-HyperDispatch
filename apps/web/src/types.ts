import type { DispatchEvent, Driver, Rider, RideRequest, WorldSnapshot } from './api/types'

export type TraceSpan = {
  trace_id: string
  span_id: string
  parent_span_id?: string
  name: string
  start_ns: number
  end_ns: number
  tags: Record<string, unknown>
  logs: string[]
}

export type WorldState = {
  snapshot?: WorldSnapshot
  events: DispatchEvent[]
  traces: TraceSpan[]
  connected: boolean
}

export const emptyState: WorldState = {
  events: [],
  traces: [],
  connected: false,
}

export function buildMockSnapshot(ts = Date.now()): WorldSnapshot {
  const drivers: Driver[] = new Array(14).fill(null).map((_, i) => ({
    id: `d-${i}`,
    status: i % 5 === 0 ? 'ENROUTE' : 'AVAILABLE',
    lat: 37.72 + (i % 7) * 0.02,
    lon: -122.52 + Math.floor(i / 7) * 0.04,
    heading: i * 21,
    speed_mps: 7 + (i % 5),
    last_update_ts: ts,
    city_id: 'sf',
  }))
  const riders: Rider[] = new Array(8).fill(null).map((_, i) => ({
    id: `r-${i}`,
    status: i % 2 ? 'WAITING' : 'MATCHED',
    lat: 37.74 + (i % 4) * 0.02,
    lon: -122.48 + Math.floor(i / 4) * 0.03,
    request_ts: ts - i * 2000,
    city_id: 'sf',
  }))
  const requests: RideRequest[] = riders.map((r, i) => ({
    id: `req-${i}`,
    rider_id: r.id,
    created_ts: ts - i * 1000,
    max_pickup_km: 3,
    city_id: 'sf',
    pickup_lat: r.lat,
    pickup_lon: r.lon,
    dropoff_lat: r.lat + 0.01,
    dropoff_lon: r.lon + 0.01,
  }))
  return { ts, drivers, riders, requests }
}
