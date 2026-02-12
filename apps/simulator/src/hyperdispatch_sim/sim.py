from __future__ import annotations

import random
import time

from hyperdispatch_protocol import Driver, DriverStatus, RidePreferences, RideRequest

from .scenarios import get_scenario


class DeterministicSim:
    def __init__(self, seed: int = 1337, city_id: str = "sf", scenario: str = "baseline_city"):
        self.rng = random.Random(seed)
        self.city_id = city_id
        self.scenario = get_scenario(scenario)

    def _hotspot(self) -> tuple[float, float]:
        if self.rng.random() < self.scenario.hotspot_bias:
            return 37.78 + self.rng.uniform(-0.01, 0.01), -122.41 + self.rng.uniform(-0.015, 0.015)
        return 37.70 + self.rng.random() * 0.15, -122.52 + self.rng.random() * 0.17

    def spawn_drivers(self, n: int) -> list[Driver]:
        now = int(time.time() * 1000)
        items: list[Driver] = []
        for i in range(n):
            lat, lon = self._hotspot()
            items.append(
                Driver(
                    id=f"d{i}",
                    status=DriverStatus.AVAILABLE,
                    lat=lat,
                    lon=lon,
                    heading=self.rng.random() * 360,
                    speed_mps=(6 + self.rng.random() * 8) * self.scenario.speed_factor,
                    last_update_ts=now,
                    city_id=self.city_id,
                    idle_since_ts=now - self.rng.randint(0, 120_000),
                )
            )
        return items

    def request(self, idx: int) -> RideRequest:
        now = int(time.time() * 1000)
        pickup_lat, pickup_lon = self._hotspot()
        dropoff_lat, dropoff_lon = self._hotspot()
        return RideRequest(
            id=f"req-{idx}",
            rider_id=f"r-{idx}",
            created_ts=now,
            max_pickup_km=2.2 + self.rng.random() * self.scenario.demand_rate,
            preferences=RidePreferences(quiet_mode=bool(idx % 2), accessibility=bool(idx % 3 == 0)),
            city_id=self.city_id,
            pickup_lat=pickup_lat,
            pickup_lon=pickup_lon,
            dropoff_lat=dropoff_lat,
            dropoff_lon=dropoff_lon,
        )
