import type { ReactNode } from 'react'

export function DataTable({ columns, rows }: { columns: string[]; rows: ReactNode[][] }) {
  return (
    <div className="panel" style={{ overflow: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            {columns.map((c) => <th key={c} style={{ textAlign: 'left', padding: 10, borderBottom: '1px solid #223140' }}>{c}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => <td key={j} style={{ padding: 10, borderBottom: '1px solid #1a2836' }}>{cell}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
