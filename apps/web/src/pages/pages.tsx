import { MapContainer, Marker, TileLayer } from 'react-leaflet'
import { useWorld } from '../store/world-store'

export function LiveMapPage() {
  const { state } = useWorld()
  const s = state.snapshot
  return <div><h3>Live Map</h3><MapContainer center={[37.77,-122.42]} zoom={13} style={{height:420}}><TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"/>{s?.drivers.map(d => <Marker key={d.id} position={[d.location.lat,d.location.lng]}/>)}{s?.riders.map(r => <Marker key={r.id} position={[r.location.lat,r.location.lng]}/>)}</MapContainer></div>
}

const simple = (name: string) => function Page(){ const {state}=useWorld(); return <div><h3>{name}</h3><pre>{JSON.stringify(state.snapshot,null,2).slice(0,1200)}</pre></div> }

export const DispatchPage = simple('Dispatch Console')
export const DriversPage = simple('Drivers')
export const RidersPage = simple('Riders')
export const TripsPage = simple('Trips')
export const MetricsPage = simple('Metrics')
export const TracesPage = simple('Traces')
export const GeoPage = simple('Geo Debugger')
export const SimulatorPage = simple('Simulator Control')
export const SettingsPage = simple('Settings')
