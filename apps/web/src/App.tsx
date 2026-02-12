import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { useWorldWS } from './hooks/useWorldWS'
import { Layout } from './components/Layout'
import { DispatchPage, DriversPage, GeoPage, LiveMapPage, MetricsPage, RidersPage, SettingsPage, SimulatorPage, TracesPage, TripsPage } from './pages/pages'

export default function App() {
  useWorldWS()
  return <BrowserRouter><Routes><Route element={<Layout/>}>
    <Route path="/" element={<Navigate to="/map"/>}/>
    <Route path="/map" element={<LiveMapPage/>}/>
    <Route path="/dispatch" element={<DispatchPage/>}/>
    <Route path="/drivers" element={<DriversPage/>}/>
    <Route path="/riders" element={<RidersPage/>}/>
    <Route path="/trips" element={<TripsPage/>}/>
    <Route path="/metrics" element={<MetricsPage/>}/>
    <Route path="/traces" element={<TracesPage/>}/>
    <Route path="/geo" element={<GeoPage/>}/>
    <Route path="/sim" element={<SimulatorPage/>}/>
    <Route path="/settings" element={<SettingsPage/>}/>
  </Route></Routes></BrowserRouter>
}
