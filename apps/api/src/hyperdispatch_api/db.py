from __future__ import annotations

import sqlite3
from pathlib import Path


class DB:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA busy_timeout=3000;")
        self._init()

    def _init(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS drivers (
              id TEXT PRIMARY KEY,
              lat REAL, lng REAL, heading_deg REAL, speed_mps REAL,
              status TEXT, last_update_ms INTEGER
            );
            CREATE TABLE IF NOT EXISTS riders (
              id TEXT PRIMARY KEY,
              lat REAL, lng REAL, status TEXT, requested_at_ms INTEGER
            );
            CREATE TABLE IF NOT EXISTS trips (
              id TEXT PRIMARY KEY,
              rider_id TEXT, driver_id TEXT, status TEXT,
              pickup_lat REAL, pickup_lng REAL, dropoff_lat REAL, dropoff_lng REAL,
              created_at_ms INTEGER
            );
            CREATE TABLE IF NOT EXISTS traces (
              trace_id TEXT, span_id TEXT, parent_id TEXT,
              name TEXT, start_ms INTEGER, end_ms INTEGER, attrs_json TEXT
            );
            """
        )
        self.conn.commit()

    def reset(self) -> None:
        self.conn.executescript("DELETE FROM drivers; DELETE FROM riders; DELETE FROM trips; DELETE FROM traces;")
        self.conn.commit()
