export type LatLng = { lat: number; lng: number }
export type Driver = { id: string; location: LatLng; heading_deg: number; speed_mps: number; status: string; last_update_ms: number }
export type Rider = { id: string; location: LatLng; status: string; requested_at_ms: number }
export type Trip = { id: string; rider_id: string; driver_id: string; status: string; pickup: LatLng; dropoff: LatLng; created_at_ms: number }
export type Metrics = { matches_per_min: number; avg_pickup_eta_s: number; waiting_riders: number; available_drivers: number; match_failures: number; retries: number }
export type Snapshot = { ts_ms: number; drivers: Driver[]; riders: Rider[]; trips: Trip[]; metrics: Metrics }
