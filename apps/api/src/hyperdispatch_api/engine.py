from __future__ import annotations

import asyncio
import json
import time
import uuid
from collections import deque
from pathlib import Path

from hyperdispatch_geo import GridIndex
from hyperdispatch_geo.grid import haversine_m
from hyperdispatch_protocol import (
    Driver,
    DriverStatus,
    LatLng,
    MatchDecision,
    MatchRequest,
    Rider,
    RiderStatus,
    TraceSpan,
    Trip,
    TripStatus,
    WorldMetrics,
    WorldSnapshot,
)

from .db import DB


class DispatchEngine:
    def __init__(self, db_path: Path):
        self.db = DB(db_path)
        self.grid = GridIndex(300)
        self.driver_locks: dict[str, asyncio.Lock] = {}
        self.metrics_window = deque(maxlen=1000)
        self.ws_clients = set()

    def _now(self) -> int:
        return int(time.time() * 1000)

    def list_drivers(self) -> list[Driver]:
        rows = self.db.conn.execute("SELECT * FROM drivers").fetchall()
        return [Driver(id=r["id"], location=LatLng(lat=r["lat"], lng=r["lng"]), heading_deg=r["heading_deg"], speed_mps=r["speed_mps"], status=DriverStatus(r["status"]), last_update_ms=r["last_update_ms"]) for r in rows]

    def list_riders(self) -> list[Rider]:
        rows = self.db.conn.execute("SELECT * FROM riders").fetchall()
        return [Rider(id=r["id"], location=LatLng(lat=r["lat"], lng=r["lng"]), status=RiderStatus(r["status"]), requested_at_ms=r["requested_at_ms"]) for r in rows]

    def list_trips(self) -> list[Trip]:
        rows = self.db.conn.execute("SELECT * FROM trips").fetchall()
        return [Trip(id=r["id"], rider_id=r["rider_id"], driver_id=r["driver_id"], status=TripStatus(r["status"]), pickup=LatLng(lat=r["pickup_lat"], lng=r["pickup_lng"]), dropoff=LatLng(lat=r["dropoff_lat"], lng=r["dropoff_lng"]), created_at_ms=r["created_at_ms"]) for r in rows]

    def upsert_driver(self, driver: Driver) -> None:
        self.db.conn.execute(
            """INSERT INTO drivers(id,lat,lng,heading_deg,speed_mps,status,last_update_ms)
            VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET lat=excluded.lat,lng=excluded.lng,heading_deg=excluded.heading_deg,speed_mps=excluded.speed_mps,status=excluded.status,last_update_ms=excluded.last_update_ms""",
            (driver.id, driver.location.lat, driver.location.lng, driver.heading_deg, driver.speed_mps, driver.status.value, driver.last_update_ms),
        )
        self.db.conn.commit()
        if driver.status == DriverStatus.AVAILABLE:
            self.grid.upsert_driver(driver.id, driver.location.lat, driver.location.lng)
        else:
            self.grid.remove_driver(driver.id)

    def _save_spans(self, spans: list[TraceSpan]) -> None:
        for s in spans:
            self.db.conn.execute(
                "INSERT INTO traces(trace_id,span_id,parent_id,name,start_ms,end_ms,attrs_json) VALUES(?,?,?,?,?,?,?)",
                (s.trace_id, s.span_id, s.parent_id, s.name, s.start_ms, s.end_ms, json.dumps(s.attrs)),
            )
        self.db.conn.commit()

    async def request_ride(self, req: MatchRequest) -> MatchDecision:
        now = self._now()
        self.db.conn.execute(
            "INSERT OR REPLACE INTO riders(id,lat,lng,status,requested_at_ms) VALUES(?,?,?,?,?)",
            (req.rider_id, req.pickup.lat, req.pickup.lng, RiderStatus.WAITING.value, now),
        )
        self.db.conn.commit()
        trace_id = str(uuid.uuid4())
        spans: list[TraceSpan] = []
        candidates = self.grid.find_nearest(req.pickup.lat, req.pickup.lng, radius_km=3, limit=20)
        retries = 0
        for candidate_id, distance_m in candidates:
            lock = self.driver_locks.setdefault(candidate_id, asyncio.Lock())
            start = self._now()
            async with lock:
                row = self.db.conn.execute("SELECT status,lat,lng FROM drivers WHERE id=?", (candidate_id,)).fetchone()
                if not row or row["status"] != DriverStatus.AVAILABLE.value:
                    retries += 1
                    spans.append(TraceSpan(trace_id=trace_id, span_id=str(uuid.uuid4()), name="candidate_rejected", start_ms=start, end_ms=self._now(), attrs={"driver_id": candidate_id}, parent_id=None))
                    continue
                trip_id = str(uuid.uuid4())
                self.db.conn.execute("UPDATE drivers SET status=? WHERE id=?", (DriverStatus.MATCHED.value, candidate_id))
                self.db.conn.execute("UPDATE riders SET status=? WHERE id=?", (RiderStatus.MATCHED.value, req.rider_id))
                self.db.conn.execute(
                    "INSERT INTO trips(id,rider_id,driver_id,status,pickup_lat,pickup_lng,dropoff_lat,dropoff_lng,created_at_ms) VALUES(?,?,?,?,?,?,?,?,?)",
                    (trip_id, req.rider_id, candidate_id, TripStatus.MATCHED.value, req.pickup.lat, req.pickup.lng, req.dropoff.lat, req.dropoff.lng, now),
                )
                self.db.conn.commit()
                self.grid.remove_driver(candidate_id)
                eta_s = distance_m / 8
                spans.append(TraceSpan(trace_id=trace_id, span_id=str(uuid.uuid4()), name="match_success", start_ms=start, end_ms=self._now(), attrs={"driver_id": candidate_id, "distance_m": distance_m}, parent_id=None))
                self._save_spans(spans)
                self.metrics_window.append({"ts": now, "eta": eta_s, "matched": 1, "fail": 0, "retry": retries})
                return MatchDecision(trip_id=trip_id, driver_id=candidate_id, rider_id=req.rider_id, pickup_eta_s=eta_s, distance_m=distance_m, trace_id=trace_id)
        self._save_spans(spans)
        self.metrics_window.append({"ts": now, "eta": 0, "matched": 0, "fail": 1, "retry": retries})
        raise ValueError("no available driver")

    def metrics(self) -> WorldMetrics:
        now = self._now()
        window = [m for m in self.metrics_window if now - m["ts"] <= 60_000]
        matched = sum(x["matched"] for x in window)
        etas = [x["eta"] for x in window if x["eta"] > 0]
        return WorldMetrics(
            matches_per_min=float(matched),
            avg_pickup_eta_s=float(sum(etas) / len(etas)) if etas else 0,
            waiting_riders=len([r for r in self.list_riders() if r.status == RiderStatus.WAITING]),
            available_drivers=len([d for d in self.list_drivers() if d.status == DriverStatus.AVAILABLE]),
            match_failures=sum(x["fail"] for x in window),
            retries=sum(x["retry"] for x in window),
        )

    def snapshot(self) -> WorldSnapshot:
        return WorldSnapshot(ts_ms=self._now(), drivers=self.list_drivers(), riders=self.list_riders(), trips=self.list_trips(), metrics=self.metrics())

    def trace(self, trace_id: str) -> list[dict]:
        rows = self.db.conn.execute("SELECT * FROM traces WHERE trace_id=?", (trace_id,)).fetchall()
        return [dict(r) for r in rows]
