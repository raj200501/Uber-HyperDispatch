import { Card } from '../components/ui/Card'
import { MetricTile } from '../components/ui/MetricTile'
import { useWorld } from '../store/world-store'

export function AnalyticsPage() {
  const { state } = useWorld()
  const matched = state.events.filter((event) => event.type === 'MATCHED').length
  const requests = state.snapshot?.requests.length ?? 0
  const drivers = state.snapshot?.drivers.length ?? 0

  return (
    <div className="page-grid page-grid--metrics">
      <MetricTile label="Matches" value={String(matched)} trend="+8%" />
      <MetricTile label="Open Requests" value={String(requests)} trend="-2%" />
      <MetricTile label="Active Drivers" value={String(drivers)} trend="+4%" />
      <MetricTile label="P95 Match Latency" value="118ms" trend="-11ms" />
      <Card title="Analytics Notes" subtitle="Operational hints derived from current simulation stream.">
        <ul>
          <li>High dispatch density in downtown core between 08:00-09:00 local.</li>
          <li>Supply surplus detected around the western perimeter of market cells.</li>
          <li>Trace spans show scoring stage dominating match SLA over network overhead.</li>
        </ul>
      </Card>
    </div>
  )
}
