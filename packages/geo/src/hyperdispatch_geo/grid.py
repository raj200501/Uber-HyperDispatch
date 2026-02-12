from __future__ import annotations

import math
from collections import defaultdict


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371000
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    d1 = math.radians(lat2 - lat1)
    d2 = math.radians(lng2 - lng1)
    a = math.sin(d1 / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(d2 / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class GridIndex:
    def __init__(self, cell_size_m: float = 300):
        self.cell_size_m = cell_size_m
        self._cells: dict[tuple[int, int], set[str]] = defaultdict(set)
        self._driver_loc: dict[str, tuple[float, float]] = {}

    def _cell(self, lat: float, lng: float) -> tuple[int, int]:
        lat_m = lat * 111_320
        lng_m = lng * (111_320 * math.cos(math.radians(lat)))
        return int(lat_m // self.cell_size_m), int(lng_m // self.cell_size_m)

    def upsert_driver(self, driver_id: str, lat: float, lng: float) -> None:
        old = self._driver_loc.get(driver_id)
        if old:
            self._cells[self._cell(old[0], old[1])].discard(driver_id)
        self._driver_loc[driver_id] = (lat, lng)
        self._cells[self._cell(lat, lng)].add(driver_id)

    def remove_driver(self, driver_id: str) -> None:
        old = self._driver_loc.pop(driver_id, None)
        if old:
            self._cells[self._cell(old[0], old[1])].discard(driver_id)

    def find_nearest(self, lat: float, lng: float, radius_km: float = 3, limit: int = 10) -> list[tuple[str, float]]:
        max_ring = max(1, int((radius_km * 1000) // self.cell_size_m) + 1)
        c0, c1 = self._cell(lat, lng)
        candidates: set[str] = set()
        for ring in range(max_ring + 1):
            for dx in range(-ring, ring + 1):
                for dy in range(-ring, ring + 1):
                    if ring > 0 and abs(dx) != ring and abs(dy) != ring:
                        continue
                    candidates |= self._cells.get((c0 + dx, c1 + dy), set())
            if len(candidates) >= limit:
                break
        dist = []
        for driver_id in candidates:
            dlat, dlng = self._driver_loc[driver_id]
            m = haversine_m(lat, lng, dlat, dlng)
            if m <= radius_km * 1000:
                dist.append((driver_id, m))
        dist.sort(key=lambda x: x[1])
        return dist[:limit]
