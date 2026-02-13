import { Card } from '../components/ui/Card'

export function SettingsPage() {
  return (
    <Card title="Settings" subtitle="Dispatch strategy configuration and visual preferences">
      <div className="control-grid">
        <label>
          Search Radius (km)
          <input defaultValue={3.4} />
        </label>
        <label>
          Fairness Weight
          <input defaultValue={0.25} />
        </label>
        <label>
          Driver Staleness TTL (ms)
          <input defaultValue={30000} />
        </label>
      </div>
    </Card>
  )
}
