import { NavLink, Outlet } from 'react-router-dom'
import { useWorld } from '../store/world-store'

const navItems = [
  ['map', 'Live Map'],
  ['dispatch-queue', 'Dispatch Queue'],
  ['matching-analytics', 'Matching Analytics'],
  ['heatmap', 'Supply vs Demand'],
  ['drivers', 'Driver Explorer'],
  ['riders', 'Rider Explorer'],
  ['replay', 'Replay Studio'],
  ['traces', 'Trace Explorer'],
  ['incidents', 'Incidents'],
  ['simulator', 'Simulator Control'],
  ['geo-debugger', 'Geo Index Debugger'],
  ['settings', 'Settings'],
  ['ui-kit', 'UI Kit'],
]

export function Layout() {
  const { state } = useWorld()
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', minHeight: '100vh' }}>
      <aside style={{ padding: 14, borderRight: '1px solid #223140', background: '#101722' }}>
        <h2 style={{ marginTop: 0 }}>Uber HyperDispatch</h2>
        <p className="muted">Control Tower</p>
        {navItems.map(([path, label]) => (
          <div key={path} style={{ marginBottom: 8 }}>
            <NavLink to={`/${path}`}>{label}</NavLink>
          </div>
        ))}
      </aside>
      <main style={{ padding: 14 }}>
        <div className="panel" style={{ marginBottom: 12, padding: 10, display: 'flex', justifyContent: 'space-between' }}>
          <span>Status: {state.connected ? 'Connected' : 'Offline'}</span>
          <span className="muted">Drivers: {state.snapshot?.drivers.length ?? 0} | Riders: {state.snapshot?.riders.length ?? 0}</span>
        </div>
        <Outlet />
      </main>
    </div>
  )
}
