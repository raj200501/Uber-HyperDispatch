export type DriverStatus = 'AVAILABLE' | 'ENROUTE' | 'ON_TRIP' | 'OFFLINE'
export type RiderStatus = 'WAITING' | 'MATCHED' | 'PICKED_UP' | 'DROPPED_OFF' | 'CANCELED'

export type Driver = {
  id: string
  status: DriverStatus
  lat: number
  lon: number
  heading: number
  speed_mps: number
  last_update_ts: number
  city_id: string
}

export type Rider = {
  id: string
  status: RiderStatus
  lat: number
  lon: number
  request_ts: number
  city_id: string
}

export type RideRequest = {
  id: string
  rider_id: string
  created_ts: number
  max_pickup_km: number
  city_id: string
  pickup_lat: number
  pickup_lon: number
  dropoff_lat: number
  dropoff_lon: number
}

export type DispatchEvent = {
  ts: number
  type: string
  city_id: string
  payload: Record<string, unknown>
}

export type WorldSnapshot = {
  ts: number
  drivers: Driver[]
  riders: Rider[]
  requests: RideRequest[]
}
