import { Card } from '../components/ui/Card'
import { DataTable } from '../components/ui/DataTable'

export function GeoDebuggerPage() {
  return (
    <Card title="Geo Debugger" subtitle="Inspect index neighborhood scans and candidate pruning.">
      <DataTable
        columns={['Query Cell', 'Ring', 'Visited Cells', 'Scanned Drivers', 'Candidates']}
        rows={new Array(10).fill(null).map((_, idx) => [
          `8f${idx}ab`,
          String(idx + 1),
          String(14 + idx * 2),
          String(35 + idx * 4),
          String(8 + idx),
        ])}
      />
    </Card>
  )
}
