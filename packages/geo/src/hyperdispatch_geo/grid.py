from __future__ import annotations

import math
from collections import defaultdict


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class GeoGridIndex:
    def __init__(self, cell_km: float = 0.35):
        self.cell_km = cell_km
        self.cells: dict[tuple[int, int], set[str]] = defaultdict(set)
        self.positions: dict[str, tuple[float, float]] = {}
        self.index_points_scanned = 0
        self.cells_visited = 0

    def reset_counters(self) -> None:
        self.index_points_scanned = 0
        self.cells_visited = 0

    def _cell(self, lat: float, lon: float) -> tuple[int, int]:
        lat_km = lat * 111.32
        lon_km = lon * (111.32 * math.cos(math.radians(lat)))
        return int(lat_km // self.cell_km), int(lon_km // self.cell_km)

    def insert_or_update(self, point_id: str, lat: float, lon: float) -> None:
        old = self.positions.get(point_id)
        if old is not None:
            self.cells[self._cell(old[0], old[1])].discard(point_id)
        self.positions[point_id] = (lat, lon)
        self.cells[self._cell(lat, lon)].add(point_id)

    def remove(self, point_id: str) -> None:
        old = self.positions.pop(point_id, None)
        if old is not None:
            self.cells[self._cell(old[0], old[1])].discard(point_id)

    def query(self, lat: float, lon: float, radius_km: float, limit: int = 32) -> list[tuple[str, float]]:
        self.reset_counters()
        center = self._cell(lat, lon)
        max_ring = max(1, int(radius_km / self.cell_km) + 1)
        candidates: set[str] = set()
        for ring in range(max_ring + 1):
            for dx in range(-ring, ring + 1):
                for dy in range(-ring, ring + 1):
                    if ring and abs(dx) != ring and abs(dy) != ring:
                        continue
                    key = (center[0] + dx, center[1] + dy)
                    self.cells_visited += 1
                    candidates.update(self.cells.get(key, set()))
            if len(candidates) >= limit:
                break
        ranked: list[tuple[str, float]] = []
        for candidate_id in candidates:
            self.index_points_scanned += 1
            c_lat, c_lon = self.positions[candidate_id]
            dist = haversine_km(lat, lon, c_lat, c_lon)
            if dist <= radius_km:
                ranked.append((candidate_id, dist))
        ranked.sort(key=lambda v: v[1])
        return ranked[:limit]
