import { Card } from '../components/ui/Card'
import { DataTable } from '../components/ui/DataTable'
import { useWorld } from '../store/world-store'

export function DispatchQueuePage() {
  const { state } = useWorld()
  const requests = state.snapshot?.requests ?? []
  return (
    <Card title="Dispatch Queue" subtitle="Pending rider demand with score diagnostics and assignment actions.">
      <DataTable
        columns={['Request', 'Rider', 'Pickup', 'Dropoff', 'Max Pickup KM']}
        rows={requests.map((request) => [
          request.id,
          request.rider_id,
          `${request.pickup_lat.toFixed(4)}, ${request.pickup_lon.toFixed(4)}`,
          `${request.dropoff_lat.toFixed(4)}, ${request.dropoff_lon.toFixed(4)}`,
          request.max_pickup_km.toFixed(2),
        ])}
      />
    </Card>
  )
}
