import { Badge } from '../components/ui/Badge'
import { Card } from '../components/ui/Card'
import { DataTable } from '../components/ui/DataTable'
import { useWorld } from '../store/world-store'

export function DriversPage() {
  const { state } = useWorld()
  const drivers = state.snapshot?.drivers ?? []
  return (
    <Card title="Driver Console" subtitle="Live driver inventory, state, and velocity.">
      <DataTable
        columns={['Driver ID', 'Status', 'Velocity', 'Heading', 'Location']}
        rows={drivers.map((driver) => [
          driver.id,
          <Badge key={driver.id}>{driver.status}</Badge>,
          `${driver.speed_mps.toFixed(1)} m/s`,
          `${driver.heading.toFixed(0)}°`,
          `${driver.lat.toFixed(4)}, ${driver.lon.toFixed(4)}`,
        ])}
      />
    </Card>
  )
}
