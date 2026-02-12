import { createContext, useContext, useReducer } from 'react'
import type { DispatchEvent } from '../api/types'
import { buildMockSnapshot, emptyState, type TraceSpan, type WorldState } from '../types'

type Action =
  | { type: 'snapshot'; payload: ReturnType<typeof buildMockSnapshot> }
  | { type: 'events'; payload: DispatchEvent[] }
  | { type: 'trace'; payload: TraceSpan }
  | { type: 'conn'; payload: boolean }

const Ctx = createContext<{ state: WorldState; dispatch: React.Dispatch<Action> } | null>(null)

function reducer(state: WorldState, action: Action): WorldState {
  switch (action.type) {
    case 'snapshot':
      return { ...state, snapshot: action.payload }
    case 'events':
      return { ...state, events: action.payload.slice(0, 120) }
    case 'trace':
      return { ...state, traces: [action.payload, ...state.traces].slice(0, 120) }
    case 'conn':
      return { ...state, connected: action.payload }
    default:
      return state
  }
}

export function WorldProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, { ...emptyState, snapshot: buildMockSnapshot() })
  return <Ctx.Provider value={{ state, dispatch }}>{children}</Ctx.Provider>
}

export function useWorld() {
  const value = useContext(Ctx)
  if (!value) {
    throw new Error('useWorld must be used inside WorldProvider')
  }
  return value
}
