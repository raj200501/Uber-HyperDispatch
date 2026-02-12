import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { WorldProvider } from './store/world-store'
import 'leaflet/dist/leaflet.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <WorldProvider><App /></WorldProvider>
  </React.StrictMode>,
)
