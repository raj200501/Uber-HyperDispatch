from __future__ import annotations

import random
import time

from hyperdispatch_protocol import Driver, DriverStatus, RidePreferences, RideRequest


class DeterministicSim:
    def __init__(self, seed: int = 1337, city_id: str = "sf"):
        self.rng = random.Random(seed)
        self.city_id = city_id

    def spawn_drivers(self, n: int) -> list[Driver]:
        now = int(time.time() * 1000)
        items: list[Driver] = []
        for i in range(n):
            items.append(
                Driver(
                    id=f"d{i}",
                    status=DriverStatus.AVAILABLE,
                    lat=37.70 + self.rng.random() * 0.15,
                    lon=-122.52 + self.rng.random() * 0.17,
                    heading=self.rng.random() * 360,
                    speed_mps=6 + self.rng.random() * 8,
                    last_update_ts=now,
                    city_id=self.city_id,
                    idle_since_ts=now - self.rng.randint(0, 120_000),
                )
            )
        return items

    def request(self, idx: int) -> RideRequest:
        now = int(time.time() * 1000)
        return RideRequest(
            id=f"req-{idx}",
            rider_id=f"r-{idx}",
            created_ts=now,
            max_pickup_km=2.5 + self.rng.random(),
            preferences=RidePreferences(quiet_mode=bool(idx % 2), accessibility=bool(idx % 3 == 0)),
            city_id=self.city_id,
            pickup_lat=37.70 + self.rng.random() * 0.15,
            pickup_lon=-122.52 + self.rng.random() * 0.17,
            dropoff_lat=37.70 + self.rng.random() * 0.15,
            dropoff_lon=-122.52 + self.rng.random() * 0.17,
        )
