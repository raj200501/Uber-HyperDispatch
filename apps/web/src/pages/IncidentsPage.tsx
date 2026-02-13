import { Card } from '../components/ui/Card'
import { DataTable } from '../components/ui/DataTable'

export function IncidentsPage() {
  return (
    <Card title="Incidents" subtitle="Derived anomalies requiring dispatcher attention.">
      <DataTable
        columns={['Incident', 'Type', 'Severity', 'Summary']}
        rows={new Array(20).fill(null).map((_, idx) => [
          `inc-${idx}`,
          idx % 2 === 0 ? 'STARVATION' : 'GRIDLOCK',
          idx % 3 === 0 ? 'HIGH' : 'MEDIUM',
          'Service-level imbalance detected across adjacent cells.',
        ])}
      />
    </Card>
  )
}
