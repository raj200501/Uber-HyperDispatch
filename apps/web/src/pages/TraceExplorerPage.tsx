import { Card } from '../components/ui/Card'
import { useWorld } from '../store/world-store'

export function TraceExplorerPage() {
  const { state } = useWorld()
  return (
    <Card title="Trace Explorer" subtitle="Waterfall representation of dispatch spans">
      <div className="trace-list">
        {state.traces.slice(0, 32).map((trace) => {
          const durationMs = Math.max(1, (trace.end_ns - trace.start_ns) / 1_000_000)
          return (
            <div className="trace-row" key={trace.span_id}>
              <div>
                <strong>{trace.name}</strong>
                <div className="muted">{trace.trace_id}</div>
              </div>
              <div className="trace-bar" style={{ width: `${Math.min(360, durationMs * 8)}px` }} />
            </div>
          )
        })}
      </div>
    </Card>
  )
}
