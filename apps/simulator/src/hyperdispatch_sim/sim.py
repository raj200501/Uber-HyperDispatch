from __future__ import annotations

import random
import time

from hyperdispatch_protocol import Driver, DriverStatus, LatLng, MatchRequest


class DeterministicSim:
    def __init__(self, seed: int = 1337):
        self.rng = random.Random(seed)

    def spawn_drivers(self, n: int) -> list[Driver]:
        out = []
        for i in range(n):
            out.append(
                Driver(
                    id=f"d{i}",
                    location=LatLng(lat=37.76 + self.rng.random() * 0.04, lng=-122.45 + self.rng.random() * 0.06),
                    heading_deg=self.rng.random() * 360,
                    speed_mps=6 + self.rng.random() * 4,
                    status=DriverStatus.AVAILABLE,
                    last_update_ms=int(time.time() * 1000),
                )
            )
        return out

    def random_request(self, i: int) -> MatchRequest:
        return MatchRequest(
            rider_id=f"r{i}",
            pickup=LatLng(lat=37.76 + self.rng.random() * 0.04, lng=-122.45 + self.rng.random() * 0.06),
            dropoff=LatLng(lat=37.74 + self.rng.random() * 0.08, lng=-122.47 + self.rng.random() * 0.08),
            constraints={},
        )
