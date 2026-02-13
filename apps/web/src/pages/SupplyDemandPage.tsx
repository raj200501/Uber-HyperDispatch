import { Card } from '../components/ui/Card'

export function SupplyDemandPage() {
  return (
    <Card title="Supply and Demand Grid" subtitle="Cell-level load map for balancing strategy.">
      <div className="heat-grid">
        {new Array(72).fill(null).map((_, index) => (
          <div className="heat-cell" key={index} />
        ))}
      </div>
    </Card>
  )
}
