from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import asdict
from pathlib import Path

from hyperdispatch_protocol import DispatchEvent, DispatchEventType, Driver, Rider, RideRequest, TraceSpan


class DispatchRepository:
    def __init__(self, db_path: Path | str = ":memory:"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self._create()

    def _create(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS drivers (
              id TEXT PRIMARY KEY,
              status TEXT,
              lat REAL,
              lon REAL,
              heading REAL,
              speed_mps REAL,
              last_update_ts INTEGER,
              city_id TEXT,
              idle_since_ts INTEGER
            );
            CREATE TABLE IF NOT EXISTS riders (
              id TEXT PRIMARY KEY,
              status TEXT,
              lat REAL,
              lon REAL,
              request_ts INTEGER,
              city_id TEXT
            );
            CREATE TABLE IF NOT EXISTS ride_requests (
              id TEXT PRIMARY KEY,
              rider_id TEXT,
              created_ts INTEGER,
              max_pickup_km REAL,
              preferences_json TEXT,
              city_id TEXT,
              pickup_lat REAL,
              pickup_lon REAL,
              dropoff_lat REAL,
              dropoff_lon REAL
            );
            CREATE TABLE IF NOT EXISTS replay_runs (
              id TEXT PRIMARY KEY,
              seed INTEGER,
              scenario TEXT,
              city_id TEXT,
              started_ts INTEGER,
              ended_ts INTEGER
            );
            CREATE TABLE IF NOT EXISTS dispatch_events (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              run_id TEXT,
              ts INTEGER,
              type TEXT,
              city_id TEXT,
              payload_json TEXT
            );
            CREATE TABLE IF NOT EXISTS trace_spans (
              trace_id TEXT,
              span_id TEXT,
              parent_span_id TEXT,
              name TEXT,
              start_ns INTEGER,
              end_ns INTEGER,
              tags_json TEXT,
              logs_json TEXT
            );
            """
        )
        self.conn.commit()

    def put_driver(self, driver: Driver) -> None:
        self.conn.execute(
            """
            INSERT INTO drivers(id,status,lat,lon,heading,speed_mps,last_update_ts,city_id,idle_since_ts)
            VALUES(:id,:status,:lat,:lon,:heading,:speed_mps,:last_update_ts,:city_id,:idle_since_ts)
            ON CONFLICT(id) DO UPDATE SET
              status=excluded.status,
              lat=excluded.lat,
              lon=excluded.lon,
              heading=excluded.heading,
              speed_mps=excluded.speed_mps,
              last_update_ts=excluded.last_update_ts,
              city_id=excluded.city_id,
              idle_since_ts=excluded.idle_since_ts
            """,
            {
                "id": driver.id,
                "status": driver.status.value,
                "lat": driver.lat,
                "lon": driver.lon,
                "heading": driver.heading,
                "speed_mps": driver.speed_mps,
                "last_update_ts": driver.last_update_ts,
                "city_id": driver.city_id,
                "idle_since_ts": driver.idle_since_ts,
            },
        )
        self.conn.commit()

    def list_drivers(self) -> list[Driver]:
        rows = self.conn.execute("SELECT * FROM drivers").fetchall()
        from hyperdispatch_protocol import DriverStatus

        return [
            Driver(
                id=row["id"],
                status=DriverStatus(row["status"]),
                lat=row["lat"],
                lon=row["lon"],
                heading=row["heading"],
                speed_mps=row["speed_mps"],
                last_update_ts=row["last_update_ts"],
                city_id=row["city_id"],
                idle_since_ts=row["idle_since_ts"] or 0,
            )
            for row in rows
        ]

    def put_rider(self, rider: Rider) -> None:
        self.conn.execute(
            """
            INSERT INTO riders(id,status,lat,lon,request_ts,city_id)
            VALUES(:id,:status,:lat,:lon,:request_ts,:city_id)
            ON CONFLICT(id) DO UPDATE SET status=excluded.status,lat=excluded.lat,lon=excluded.lon,request_ts=excluded.request_ts,city_id=excluded.city_id
            """,
            {
                "id": rider.id,
                "status": rider.status.value,
                "lat": rider.lat,
                "lon": rider.lon,
                "request_ts": rider.request_ts,
                "city_id": rider.city_id,
            },
        )
        self.conn.commit()

    def list_riders(self) -> list[Rider]:
        rows = self.conn.execute("SELECT * FROM riders").fetchall()
        from hyperdispatch_protocol import RiderStatus

        return [
            Rider(
                id=row["id"],
                status=RiderStatus(row["status"]),
                lat=row["lat"],
                lon=row["lon"],
                request_ts=row["request_ts"],
                city_id=row["city_id"],
            )
            for row in rows
        ]

    def put_request(self, request: RideRequest) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO ride_requests(id,rider_id,created_ts,max_pickup_km,preferences_json,city_id,pickup_lat,pickup_lon,dropoff_lat,dropoff_lon)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                request.id,
                request.rider_id,
                request.created_ts,
                request.max_pickup_km,
                json.dumps(asdict(request.preferences)),
                request.city_id,
                request.pickup_lat,
                request.pickup_lon,
                request.dropoff_lat,
                request.dropoff_lon,
            ),
        )
        self.conn.commit()

    def list_requests(self) -> list[RideRequest]:
        from hyperdispatch_protocol import RidePreferences

        rows = self.conn.execute("SELECT * FROM ride_requests ORDER BY created_ts DESC").fetchall()
        out: list[RideRequest] = []
        for row in rows:
            prefs = json.loads(row["preferences_json"])
            out.append(
                RideRequest(
                    id=row["id"],
                    rider_id=row["rider_id"],
                    created_ts=row["created_ts"],
                    max_pickup_km=row["max_pickup_km"],
                    preferences=RidePreferences(**prefs),
                    city_id=row["city_id"],
                    pickup_lat=row["pickup_lat"],
                    pickup_lon=row["pickup_lon"],
                    dropoff_lat=row["dropoff_lat"],
                    dropoff_lon=row["dropoff_lon"],
                )
            )
        return out

    def start_run(self, seed: int, scenario: str, city_id: str, started_ts: int) -> str:
        run_id = str(uuid.uuid4())
        self.conn.execute(
            "INSERT INTO replay_runs(id,seed,scenario,city_id,started_ts,ended_ts) VALUES(?,?,?,?,?,NULL)",
            (run_id, seed, scenario, city_id, started_ts),
        )
        self.conn.commit()
        return run_id

    def stop_run(self, run_id: str, ended_ts: int) -> None:
        self.conn.execute("UPDATE replay_runs SET ended_ts=? WHERE id=?", (ended_ts, run_id))
        self.conn.commit()

    def list_runs(self) -> list[dict[str, object]]:
        rows = self.conn.execute("SELECT * FROM replay_runs ORDER BY started_ts DESC").fetchall()
        return [dict(r) for r in rows]

    def append_event(self, event: DispatchEvent, run_id: str | None = None) -> None:
        self.conn.execute(
            "INSERT INTO dispatch_events(run_id,ts,type,city_id,payload_json) VALUES(?,?,?,?,?)",
            (run_id, event.ts, event.type.value, event.city_id, json.dumps(event.payload)),
        )
        self.conn.commit()

    def list_events(self, from_ts: int = 0, run_id: str | None = None) -> list[DispatchEvent]:
        query = "SELECT ts,type,city_id,payload_json FROM dispatch_events WHERE ts>=?"
        params: list[object] = [from_ts]
        if run_id:
            query += " AND run_id=?"
            params.append(run_id)
        query += " ORDER BY ts"
        rows = self.conn.execute(query, tuple(params)).fetchall()
        return [
            DispatchEvent(ts=r["ts"], type=DispatchEventType(r["type"]), city_id=r["city_id"], payload=json.loads(r["payload_json"]))
            for r in rows
        ]

    def save_span(self, span: TraceSpan) -> None:
        self.conn.execute(
            "INSERT INTO trace_spans(trace_id,span_id,parent_span_id,name,start_ns,end_ns,tags_json,logs_json) VALUES(?,?,?,?,?,?,?,?)",
            (span.trace_id, span.span_id, span.parent_span_id, span.name, span.start_ns, span.end_ns, json.dumps(span.tags), json.dumps(span.logs)),
        )
        self.conn.commit()

    def list_spans(self, trace_id: str | None = None) -> list[TraceSpan]:
        params: tuple[object, ...] = ()
        sql = "SELECT * FROM trace_spans"
        if trace_id:
            sql += " WHERE trace_id=?"
            params = (trace_id,)
        rows = self.conn.execute(sql, params).fetchall()
        return [
            TraceSpan(
                trace_id=r["trace_id"],
                span_id=r["span_id"],
                parent_span_id=r["parent_span_id"],
                name=r["name"],
                start_ns=r["start_ns"],
                end_ns=r["end_ns"],
                tags=json.loads(r["tags_json"]),
                logs=json.loads(r["logs_json"]),
            )
            for r in rows
        ]
