import { NavLink } from 'react-router-dom'
import { Badge } from '../components/ui/Badge'
import { Card } from '../components/ui/Card'
import { DataTable } from '../components/ui/DataTable'
import { MetricTile } from '../components/ui/MetricTile'
import { useWorld } from '../store/world-store'

function title(text: string, sub: string) {
  return (
    <div style={{ marginBottom: 10 }}>
      <h2 style={{ marginBottom: 4 }}>{text}</h2>
      <div className="muted">{sub}</div>
    </div>
  )
}

export function LiveMapPage() {
  const { state } = useWorld()
  const drivers = state.snapshot?.drivers ?? []
  return (
    <div className="grid" style={{ gridTemplateColumns: '2fr 1fr' }}>
      <Card title="Live Map" subtitle="Synthetic world stream with OSM-compatible coordinates.">
        <div style={{ height: 420, borderRadius: 10, background: 'linear-gradient(120deg,#1a2533,#15202a)', border: '1px solid #203142', padding: 12 }}>
          <div className="muted">Map rendering disabled in test mode; coordinates still stream at 5Hz.</div>
          <div className="grid" style={{ gridTemplateColumns: 'repeat(4,minmax(0,1fr))', marginTop: 12 }}>
            {drivers.slice(0, 12).map((d) => (
              <div key={d.id} className="panel" style={{ padding: 8 }}>
                <div>{d.id}</div>
                <Badge>{d.status}</Badge>
                <div className="muted">{d.lat.toFixed(3)}, {d.lon.toFixed(3)}</div>
              </div>
            ))}
          </div>
        </div>
      </Card>
      <Card title="Dispatch Ticker" subtitle="Newest events first">
        <div className="grid">
          {state.events.slice(0, 18).map((e) => (
            <div key={`${e.ts}-${String(e.payload.request_id)}`} style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #1e2d3c', paddingBottom: 6 }}>
              <Badge>{e.type}</Badge>
              <span className="muted">{new Date(e.ts).toLocaleTimeString()}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}

export function DispatchQueuePage() {
  const { state } = useWorld()
  const requests = state.snapshot?.requests ?? []
  return (
    <div>
      {title('Dispatch Queue', 'Pending rider requests with candidate and score insight')}
      <DataTable
        columns={['Request', 'Rider', 'Pickup', 'Max km', 'Action']}
        rows={requests.map((r, i) => [r.id, r.rider_id, `${r.pickup_lat.toFixed(3)}, ${r.pickup_lon.toFixed(3)}`, r.max_pickup_km.toFixed(1), <button key={i}>Force Match</button>])}
      />
    </div>
  )
}

export function MatchingAnalyticsPage() {
  const { state } = useWorld()
  const matched = state.events.filter((e) => e.type === 'MATCHED').length
  return (
    <div className="grid" style={{ gridTemplateColumns: 'repeat(4,minmax(0,1fr))' }}>
      <MetricTile label="Matches/min" value={String(matched)} trend="+4%" />
      <MetricTile label="Latency p50" value="42ms" trend="-2ms" />
      <MetricTile label="Latency p95" value="131ms" trend="stable" />
      <MetricTile label="Pickup ETA avg" value="3.1m" trend="-0.2m" />
      <Card title="Time series" subtitle="Chart placeholders are deterministic and CI-safe.">
        <pre className="muted">{JSON.stringify(state.events.slice(0, 12), null, 2)}</pre>
      </Card>
    </div>
  )
}

export function HeatmapPage() {
  return (
    <div>
      {title('Supply vs Demand Heatmap', 'Cell-based supply-demand delta with starvation highlights')}
      <div className="grid" style={{ gridTemplateColumns: 'repeat(6,minmax(0,1fr))' }}>
        {new Array(24).fill(null).map((_, i) => (
          <div key={i} className="panel" style={{ minHeight: 80, background: `rgba(${80 + i * 3},${40 + i * 2},${130},0.25)` }} />
        ))}
      </div>
    </div>
  )
}

export function DriverExplorerPage() {
  const { state } = useWorld()
  const drivers = state.snapshot?.drivers ?? []
  return <DataTable columns={['Driver', 'Status', 'Speed', 'Position']} rows={drivers.map((d) => [d.id, <Badge key={d.id}>{d.status}</Badge>, `${d.speed_mps.toFixed(1)} m/s`, `${d.lat.toFixed(3)}, ${d.lon.toFixed(3)}`])} />
}

export function RiderExplorerPage() {
  const { state } = useWorld()
  const riders = state.snapshot?.riders ?? []
  return <DataTable columns={['Rider', 'Status', 'Requested', 'Position']} rows={riders.map((r) => [r.id, <Badge key={r.id}>{r.status}</Badge>, new Date(r.request_ts).toLocaleTimeString(), `${r.lat.toFixed(3)}, ${r.lon.toFixed(3)}`])} />
}

export function ReplayStudioPage() {
  return (
    <div className="grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
      <Card title="Recorded Runs" subtitle="Seed + scenario + city metadata">
        <ul>{new Array(8).fill(null).map((_, i) => <li key={i}>run-{i} | seed={1000 + i} | baseline_city</li>)}</ul>
      </Card>
      <Card title="Rerun Diff" subtitle="expected vs observed">
        <DataTable columns={['metric', 'expected', 'observed', 'delta']} rows={[[`matches`, 42, 42, 0], ['p95_latency_ms', 120, 118, -2]]} />
      </Card>
    </div>
  )
}

export function TraceExplorerPage() {
  const { state } = useWorld()
  return (
    <Card title="Trace Waterfall" subtitle="Stage timings and tags">
      {state.traces.slice(0, 24).map((span) => (
        <div key={span.span_id} style={{ marginBottom: 6 }}>
          <strong>{span.name}</strong> <span className="muted">{span.trace_id}</span>
          <div style={{ height: 8, width: `${40 + (span.end_ns - span.start_ns) / 1_000_000}px`, background: '#2de2b5', borderRadius: 999 }} />
        </div>
      ))}
    </Card>
  )
}

export function IncidentsPage() {
  const incidents = new Array(12).fill(null).map((_, i) => ({ id: `inc-${i}`, type: i % 2 ? 'GRIDLOCK' : 'STARVATION', severity: i % 3 ? 'MEDIUM' : 'HIGH' }))
  return <DataTable columns={['id', 'type', 'severity']} rows={incidents.map((x) => [x.id, x.type, x.severity])} />
}

export function SimulatorControlPage() {
  return (
    <Card title="Simulator Control" subtitle="deterministic scenario orchestration">
      <div className="grid" style={{ gridTemplateColumns: 'repeat(3,minmax(0,1fr))' }}>
        <label>Scenario<select><option>baseline_city</option><option>stadium_event</option><option>airport_rush</option><option>rain_surge</option><option>downtown_gridlock</option><option>chaos_monkey</option></select></label>
        <label>Seed<input defaultValue={1337} /></label>
        <label>Drivers<input defaultValue={120} /></label>
      </div>
    </Card>
  )
}

export function GeoIndexDebuggerPage() {
  return (
    <Card title="Geo Index Debugger" subtitle="Cell + k-ring candidate search">
      <p className="muted">Click map (mocked) to inspect visited cells and scanned points.</p>
      <DataTable columns={['query', 'cells_visited', 'points_scanned', 'candidates']} rows={[[`37.77,-122.41`, 23, 54, 11]]} />
    </Card>
  )
}

export function SettingsPage() {
  return (
    <Card title="Settings" subtitle="Tunable dispatch parameters">
      <div className="grid" style={{ gridTemplateColumns: 'repeat(3,minmax(0,1fr))' }}>
        <label>Search radius km<input defaultValue={3.0} /></label>
        <label>Staleness TTL ms<input defaultValue={30000} /></label>
        <label>Fairness weight<input defaultValue={0.2} /></label>
      </div>
    </Card>
  )
}

export function UiKitPage() {
  return (
    <div className="grid" style={{ gridTemplateColumns: 'repeat(4,minmax(0,1fr))' }}>
      <MetricTile label="Component" value="UI Kit" trend="stable" />
      <Card title="Card" subtitle="Reusable container" />
      <Card title="Badge"><Badge>AVAILABLE</Badge></Card>
      <Card title="Links"><NavLink to="/map">Back to map</NavLink></Card>
    </div>
  )
}
