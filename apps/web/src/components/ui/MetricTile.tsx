export function MetricTile({ label, value, trend }: { label: string; value: string; trend?: string }) {
  return (
    <div className="panel" style={{ padding: 12 }}>
      <div className="muted" style={{ fontSize: 12 }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700 }}>{value}</div>
      {trend ? <div style={{ fontSize: 12, color: '#2de2b5' }}>{trend}</div> : null}
    </div>
  )
}
