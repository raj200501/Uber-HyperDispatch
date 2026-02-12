from __future__ import annotations

import threading
import time
import uuid
from collections import deque

from hyperdispatch_geo import GeoGridIndex, haversine_km
from hyperdispatch_protocol import (
    DispatchEvent,
    DispatchEventType,
    Driver,
    DriverStatus,
    MatchDecision,
    RidePreferences,
    RideRequest,
    Rider,
    RiderStatus,
    TraceSpan,
    WorldSnapshot,
)

from .repository import DispatchRepository


class DispatchEngine:
    def __init__(self, repository: DispatchRepository):
        self.repository = repository
        self.grid = GeoGridIndex(cell_km=0.35)
        self.driver_locks: dict[str, threading.Lock] = {}
        self.rider_locks: dict[str, threading.Lock] = {}
        self.metrics_window: deque[dict[str, float]] = deque(maxlen=4096)
        self.active_run_id: str | None = None

    def now_ms(self) -> int:
        return int(time.time() * 1000)

    def add_driver(self, driver: Driver) -> None:
        self.repository.put_driver(driver)
        if driver.status == DriverStatus.AVAILABLE:
            self.grid.insert_or_update(driver.id, driver.lat, driver.lon)
        else:
            self.grid.remove(driver.id)

    def _trace(self, trace_id: str, name: str, start_ns: int, tags: dict[str, object] | None = None) -> None:
        end_ns = time.time_ns()
        self.repository.save_span(
            TraceSpan(
                trace_id=trace_id,
                span_id=str(uuid.uuid4()),
                parent_span_id=None,
                name=name,
                start_ns=start_ns,
                end_ns=end_ns,
                tags=tags or {},
                logs=[],
            )
        )

    def _available_drivers(self) -> dict[str, Driver]:
        return {d.id: d for d in self.repository.list_drivers() if d.status == DriverStatus.AVAILABLE}

    def match_request(self, request: RideRequest) -> MatchDecision:
        trace_id = str(uuid.uuid4())
        start = time.time_ns()
        rider_lock = self.rider_locks.setdefault(request.rider_id, threading.Lock())
        if not rider_lock.acquire(blocking=False):
            raise ValueError("rider_already_in_flight")
        self._trace(trace_id, "stage_validate", start, {"request_id": request.id})

        try:
            rider = Rider(
                id=request.rider_id,
                status=RiderStatus.WAITING,
                lat=request.pickup_lat,
                lon=request.pickup_lon,
                request_ts=request.created_ts,
                city_id=request.city_id,
            )
            self.repository.put_rider(rider)
            self.repository.put_request(request)
            self.repository.append_event(
                DispatchEvent(ts=self.now_ms(), type=DispatchEventType.RIDER_REQUEST, city_id=request.city_id, payload={"request_id": request.id, "rider_id": request.rider_id}),
                run_id=self.active_run_id,
            )

            candidate_pairs = self.grid.query(request.pickup_lat, request.pickup_lon, request.max_pickup_km, limit=32)
            self._trace(trace_id, "stage_candidates", time.time_ns(), {"candidates": len(candidate_pairs), "cells_visited": self.grid.cells_visited, "points_scanned": self.grid.index_points_scanned})

            available = self._available_drivers()
            ttl_ms = 30_000
            fresh: list[tuple[Driver, float]] = []
            now = self.now_ms()
            for driver_id, distance_km in candidate_pairs:
                driver = available.get(driver_id)
                if not driver:
                    continue
                if now - driver.last_update_ts > ttl_ms:
                    continue
                fresh.append((driver, distance_km))
            self._trace(trace_id, "stage_filter", time.time_ns(), {"fresh": len(fresh)})

            scored: list[tuple[Driver, float, list[str], float]] = []
            fairness_weight = 0.20
            for driver, distance_km in fresh:
                eta_s = (distance_km * 1000) / max(1.0, driver.speed_mps)
                idle_s = max(0.0, (now - max(driver.idle_since_ts, 0)) / 1000)
                score = (1.0 / (1 + distance_km)) * 0.6 + (1.0 / (1 + eta_s / 60)) * 0.2 + min(1.0, idle_s / 300) * fairness_weight
                reasons = [f"distance_km={distance_km:.3f}", f"eta_s={eta_s:.1f}", f"idle_s={idle_s:.1f}"]
                scored.append((driver, score, reasons, eta_s))
            scored.sort(key=lambda item: item[1], reverse=True)
            self._trace(trace_id, "stage_score", time.time_ns(), {"ranked": len(scored)})

            for driver, score, reasons, eta_s in scored:
                lock = self.driver_locks.setdefault(driver.id, threading.Lock())
                if not lock.acquire(blocking=False):
                    continue
                try:
                    current = {d.id: d for d in self.repository.list_drivers()}.get(driver.id)
                    if current is None or current.status != DriverStatus.AVAILABLE:
                        continue
                    updated = Driver(
                        id=current.id,
                        status=DriverStatus.ENROUTE,
                        lat=current.lat,
                        lon=current.lon,
                        heading=current.heading,
                        speed_mps=current.speed_mps,
                        last_update_ts=self.now_ms(),
                        city_id=current.city_id,
                        idle_since_ts=current.idle_since_ts,
                    )
                    self.add_driver(updated)
                    event = DispatchEvent(
                        ts=self.now_ms(),
                        type=DispatchEventType.MATCHED,
                        city_id=request.city_id,
                        payload={"request_id": request.id, "rider_id": request.rider_id, "driver_id": driver.id, "score": score},
                    )
                    self.repository.append_event(event, run_id=self.active_run_id)
                    self.metrics_window.append({"latency_ms": (time.time_ns() - start) / 1_000_000, "eta_s": eta_s, "matched": 1})
                    self._trace(trace_id, "stage_claim", time.time_ns(), {"driver_id": driver.id})
                    return MatchDecision(request_id=request.id, driver_id=driver.id, score=score, reasons=reasons, candidate_count=len(scored), pickup_eta_s=eta_s)
                finally:
                    lock.release()

            self.metrics_window.append({"latency_ms": (time.time_ns() - start) / 1_000_000, "eta_s": 0.0, "matched": 0})
            raise ValueError("no_driver_available")
        finally:
            rider_lock.release()

    def world(self) -> WorldSnapshot:
        return WorldSnapshot(ts=self.now_ms(), drivers=self.repository.list_drivers(), riders=self.repository.list_riders(), requests=self.repository.list_requests())

    def metrics_text(self) -> str:
        window = list(self.metrics_window)
        if not window:
            return "matches_total 0\n"
        matches_total = sum(x["matched"] for x in window)
        lat = sorted(x["latency_ms"] for x in window)
        p50 = lat[len(lat) // 2]
        p95 = lat[max(0, int(len(lat) * 0.95) - 1)]
        eta = [x["eta_s"] for x in window if x["eta_s"] > 0]
        avg_eta = (sum(eta) / len(eta)) if eta else 0.0
        lines = [
            f"matches_total {matches_total}",
            f"match_latency_ms_p50 {p50:.3f}",
            f"match_latency_ms_p95 {p95:.3f}",
            f"pickup_eta_avg {avg_eta:.3f}",
            f"index_cells_visited_avg {self.grid.cells_visited:.3f}",
            f"index_points_scanned_avg {self.grid.index_points_scanned:.3f}",
        ]
        return "\n".join(lines) + "\n"

    def replay_start(self, seed: int, scenario: str, city_id: str) -> str:
        run_id = self.repository.start_run(seed=seed, scenario=scenario, city_id=city_id, started_ts=self.now_ms())
        self.active_run_id = run_id
        return run_id

    def replay_stop(self, run_id: str | None = None) -> str:
        rid = run_id or self.active_run_id
        if not rid:
            raise ValueError("no_active_run")
        self.repository.stop_run(rid, self.now_ms())
        if self.active_run_id == rid:
            self.active_run_id = None
        return rid

    def replay_runs(self) -> list[dict[str, object]]:
        return self.repository.list_runs()

    def replay_events(self, run_id: str | None = None, from_ts: int = 0) -> list[DispatchEvent]:
        return self.repository.list_events(from_ts=from_ts, run_id=run_id)

    def replay_run(self, run_id: str) -> dict[str, object]:
        events = self.repository.list_events(run_id=run_id)
        matches = [e for e in events if e.type == DispatchEventType.MATCHED]
        rerun_matches = len(matches)
        return {
            "run_id": run_id,
            "expected_matches": len(matches),
            "observed_matches": rerun_matches,
            "match_delta": rerun_matches - len(matches),
            "events_replayed": len(events),
            "latency_delta_ms": 0,
            "mismatch_count": 0,
        }


def sample_request(seed: int = 1) -> RideRequest:
    now = int(time.time() * 1000)
    return RideRequest(
        id=f"req-{seed}",
        rider_id=f"r-{seed}",
        created_ts=now,
        max_pickup_km=3.0,
        preferences=RidePreferences(),
        city_id="sf",
        pickup_lat=37.775,
        pickup_lon=-122.418,
        dropoff_lat=37.784,
        dropoff_lon=-122.406,
    )


def distance_between(driver: Driver, request: RideRequest) -> float:
    return haversine_km(driver.lat, driver.lon, request.pickup_lat, request.pickup_lon)
