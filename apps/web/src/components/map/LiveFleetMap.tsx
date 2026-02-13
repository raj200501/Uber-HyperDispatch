import { useMemo } from 'react'
import { MapContainer, Marker, Polyline, TileLayer } from 'react-leaflet'
import L from 'leaflet'
import type { Driver, Rider } from '../../api/types'

type Props = {
  drivers: Driver[]
  riders: Rider[]
}

const driverIcon = (status: string) =>
  L.divIcon({
    className: 'driver-icon',
    html: `<span class="driver-dot ${status.toLowerCase()}"></span>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  })

const riderIcon = L.divIcon({
  className: 'rider-icon',
  html: '<span class="rider-dot"></span>',
  iconSize: [14, 14],
  iconAnchor: [7, 7],
})

export function LiveFleetMap({ drivers, riders }: Props) {
  const center = useMemo<[number, number]>(() => {
    if (drivers.length > 0) {
      return [drivers[0].lat, drivers[0].lon]
    }
    return [37.7749, -122.4194]
  }, [drivers])

  return (
    <div className="map-shell">
      <MapContainer center={center} zoom={12} scrollWheelZoom style={{ height: 520, width: '100%' }}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {drivers.map((driver) => (
          <Marker key={driver.id} position={[driver.lat, driver.lon]} icon={driverIcon(driver.status)} />
        ))}
        {riders.map((rider) => (
          <Marker key={rider.id} position={[rider.lat, rider.lon]} icon={riderIcon} />
        ))}
        {drivers.slice(0, Math.min(drivers.length, riders.length)).map((driver, idx) => {
          const rider = riders[idx]
          return (
            <Polyline
              key={`${driver.id}-${rider.id}`}
              positions={[
                [driver.lat, driver.lon],
                [rider.lat, rider.lon],
              ]}
              color="var(--accent)"
              weight={1}
              opacity={0.45}
            />
          )
        })}
      </MapContainer>
    </div>
  )
}
