import { createContext, useContext, useReducer } from 'react'
import type { Snapshot } from '../types'

type State = { snapshot?: Snapshot; connected: boolean }
type Action = { type: 'snapshot'; payload: Snapshot } | { type: 'conn'; payload: boolean }

const Ctx = createContext<{state: State; dispatch: React.Dispatch<Action>} | null>(null)

function reducer(state: State, action: Action): State {
  if (action.type === 'snapshot') return { ...state, snapshot: action.payload }
  if (action.type === 'conn') return { ...state, connected: action.payload }
  return state
}

export function WorldProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(reducer, { connected: false })
  return <Ctx.Provider value={{ state, dispatch }}>{children}</Ctx.Provider>
}

export function useWorld() {
  const v = useContext(Ctx)
  if (!v) throw new Error('missing provider')
  return v
}
