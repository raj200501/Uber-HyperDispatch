import { Card } from '../components/ui/Card'

export function SimulatorControlPage() {
  return (
    <Card title="Simulator Control" subtitle="Deterministic scenario runtime configuration">
      <div className="control-grid">
        <label>
          Scenario
          <select defaultValue="baseline_city">
            <option value="baseline_city">baseline_city</option>
            <option value="airport_rush">airport_rush</option>
            <option value="rain_surge">rain_surge</option>
            <option value="stadium_event">stadium_event</option>
          </select>
        </label>
        <label>
          Seed
          <input type="number" defaultValue={1337} />
        </label>
        <label>
          Max Steps
          <input type="number" defaultValue={300} />
        </label>
      </div>
    </Card>
  )
}
