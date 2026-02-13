import { Badge } from '../components/ui/Badge'
import { Card } from '../components/ui/Card'
import { LiveFleetMap } from '../components/map/LiveFleetMap'
import { useWorld } from '../store/world-store'

export function LiveMapPage() {
  const { state } = useWorld()
  const drivers = state.snapshot?.drivers ?? []
  const riders = state.snapshot?.riders ?? []

  return (
    <div className="page-grid page-grid--map">
      <Card title="Live Operations Map" subtitle="Real-time driver and rider telemetry over OpenStreetMap tiles.">
        <LiveFleetMap drivers={drivers} riders={riders} />
      </Card>
      <Card title="Event Ticker" subtitle="Most recent dispatch events">
        <div className="ticker-list">
          {state.events.slice(0, 24).map((event) => (
            <div className="ticker-row" key={`${event.ts}-${event.type}-${String(event.payload.request_id ?? '')}`}>
              <Badge>{event.type}</Badge>
              <span className="muted">{new Date(event.ts).toLocaleTimeString()}</span>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
