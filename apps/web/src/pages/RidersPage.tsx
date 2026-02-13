import { Badge } from '../components/ui/Badge'
import { Card } from '../components/ui/Card'
import { DataTable } from '../components/ui/DataTable'
import { useWorld } from '../store/world-store'

export function RidersPage() {
  const { state } = useWorld()
  const riders = state.snapshot?.riders ?? []
  return (
    <Card title="Rider Console" subtitle="Current rider demand and request lifecycle.">
      <DataTable
        columns={['Rider ID', 'Status', 'Requested At', 'Location']}
        rows={riders.map((rider) => [
          rider.id,
          <Badge key={rider.id}>{rider.status}</Badge>,
          new Date(rider.request_ts).toLocaleTimeString(),
          `${rider.lat.toFixed(4)}, ${rider.lon.toFixed(4)}`,
        ])}
      />
    </Card>
  )
}
