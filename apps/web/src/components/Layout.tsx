import { NavLink, Outlet } from 'react-router-dom'
import { useWorld } from '../store/world-store'

const navItems = [
  ['map', 'Live Map'],
  ['dispatch-queue', 'Dispatch Queue'],
  ['analytics', 'Analytics'],
  ['supply-demand', 'Supply & Demand'],
  ['drivers', 'Drivers'],
  ['riders', 'Riders'],
  ['replay', 'Replay Studio'],
  ['traces', 'Trace Explorer'],
  ['incidents', 'Incidents'],
  ['simulator', 'Simulator Control'],
  ['geo-debugger', 'Geo Debugger'],
  ['settings', 'Settings'],
]

export function Layout() {
  const { state } = useWorld()
  return (
    <div className="layout-shell">
      <aside className="sidebar">
        <h2>Uber HyperDispatch</h2>
        <p className="muted">Control Tower Console</p>
        {navItems.map(([path, label]) => (
          <div key={path} style={{ marginBottom: 8 }}>
            <NavLink to={`/${path}`}>{label}</NavLink>
          </div>
        ))}
      </aside>
      <main className="content">
        <div className="panel topbar">
          <span>Status: {state.connected ? 'Connected' : 'Offline'}</span>
          <span className="muted">Drivers: {state.snapshot?.drivers.length ?? 0} | Riders: {state.snapshot?.riders.length ?? 0}</span>
        </div>
        <Outlet />
      </main>
    </div>
  )
}
