import { Card } from '../components/ui/Card'
import { DataTable } from '../components/ui/DataTable'

export function ReplayStudioPage() {
  return (
    <div className="page-grid page-grid--split">
      <Card title="Replay Runs" subtitle="Recorded deterministic runs for regression and postmortem playback.">
        <DataTable
          columns={['Run', 'Scenario', 'Seed', 'City', 'Duration']}
          rows={new Array(12).fill(null).map((_, idx) => [
            `run-${idx}`,
            'baseline_city',
            String(1300 + idx),
            'sf',
            `${12 + idx}s`,
          ])}
        />
      </Card>
      <Card title="Timeline Scrubber" subtitle="Synthetic timeline control for event replay.">
        <div className="scrubber" />
      </Card>
    </div>
  )
}
