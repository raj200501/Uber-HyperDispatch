import type { PropsWithChildren } from 'react'

export function Card({ children, title, subtitle }: PropsWithChildren<{ title?: string; subtitle?: string }>) {
  return (
    <section className="panel" style={{ padding: 12 }}>
      {title ? <h3 style={{ margin: 0 }}>{title}</h3> : null}
      {subtitle ? <p className="muted" style={{ marginTop: 4 }}>{subtitle}</p> : null}
      {children}
    </section>
  )
}
