import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { useEventStream } from './hooks/useEventStream'
import { useTraceStream } from './hooks/useTraceStream'
import { useWorldStream } from './hooks/useWorldStream'
import {
  DispatchQueuePage,
  DriverExplorerPage,
  GeoIndexDebuggerPage,
  HeatmapPage,
  IncidentsPage,
  LiveMapPage,
  MatchingAnalyticsPage,
  ReplayStudioPage,
  RiderExplorerPage,
  SettingsPage,
  SimulatorControlPage,
  TraceExplorerPage,
  UiKitPage,
} from './pages/pages'

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
          <Route path="/matching-analytics" element={<MatchingAnalyticsPage />} />
          <Route path="/heatmap" element={<HeatmapPage />} />
          <Route path="/drivers" element={<DriverExplorerPage />} />
          <Route path="/riders" element={<RiderExplorerPage />} />
          <Route path="/replay" element={<ReplayStudioPage />} />
          <Route path="/traces" element={<TraceExplorerPage />} />
          <Route path="/incidents" element={<IncidentsPage />} />
          <Route path="/simulator" element={<SimulatorControlPage />} />
          <Route path="/geo-debugger" element={<GeoIndexDebuggerPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/ui-kit" element={<UiKitPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
