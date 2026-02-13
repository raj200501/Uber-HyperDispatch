import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { useEventStream } from './hooks/useEventStream'
import { useTraceStream } from './hooks/useTraceStream'
import { useWorldStream } from './hooks/useWorldStream'
import {
  AnalyticsPage,
  DispatchQueuePage,
  DriversPage,
  GeoDebuggerPage,
  IncidentsPage,
  LiveMapPage,
  ReplayStudioPage,
  RidersPage,
  SettingsPage,
  SimulatorControlPage,
  SupplyDemandPage,
  TraceExplorerPage,
} from './pages'

export default function App() {
  useWorldStream()
  useEventStream()
  useTraceStream()

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/map" />} />
          <Route path="/map" element={<LiveMapPage />} />
          <Route path="/dispatch-queue" element={<DispatchQueuePage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/supply-demand" element={<SupplyDemandPage />} />
          <Route path="/drivers" element={<DriversPage />} />
          <Route path="/riders" element={<RidersPage />} />
          <Route path="/replay" element={<ReplayStudioPage />} />
          <Route path="/traces" element={<TraceExplorerPage />} />
          <Route path="/incidents" element={<IncidentsPage />} />
          <Route path="/simulator" element={<SimulatorControlPage />} />
          <Route path="/geo-debugger" element={<GeoDebuggerPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
