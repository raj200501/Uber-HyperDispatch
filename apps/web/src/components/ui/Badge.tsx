import type { PropsWithChildren } from 'react'

const colors: Record<string, string> = {
  AVAILABLE: '#2de2b5',
  ENROUTE: '#6cb2ff',
  ON_TRIP: '#c090ff',
  OFFLINE: '#536b84',
  WAITING: '#f6b73c',
  MATCHED: '#6cb2ff',
  ANOMALY: '#ff6a88',
}

export function Badge({ children }: PropsWithChildren) {
  const key = String(children)
  return <span style={{ background: `${colors[key] ?? '#384b60'}22`, color: colors[key] ?? '#d8e3f2', border: `1px solid ${colors[key] ?? '#516378'}`, borderRadius: 999, padding: '2px 8px', fontSize: 12 }}>{children}</span>
}
