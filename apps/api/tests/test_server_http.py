from __future__ import annotations

import http.client
import json
import threading
import time
from http.server import HTTPServer
from pathlib import Path

from hyperdispatch_api.main import HyperDispatchApp
import hyperdispatch_api.server as server
from hyperdispatch_protocol import Driver, DriverStatus, RidePreferences, RideRequest, to_dict



def now_ms() -> int:
    return time.time_ns() // 1_000_000


class ServerHarness:
    def __init__(self, tmp_path: Path):
        self.app = HyperDispatchApp(db_path=str(tmp_path / "test.sqlite"))
        self.httpd = HTTPServer(("127.0.0.1", 0), server.Handler)
        self.port = self.httpd.server_port
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.original_app = server.app

    def __enter__(self) -> "ServerHarness":
        server.app = self.app
        self.thread.start()
        return self

    def __exit__(self, *_args: object) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2)
        server.app = self.original_app

    def request(self, method: str, path: str, body: dict[str, object] | None = None) -> tuple[int, dict[str, object] | list[object] | str]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        payload = None if body is None else json.dumps(body)
        headers = {"Content-Type": "application/json"} if payload is not None else {}
        conn.request(method, path, body=payload, headers=headers)
        response = conn.getresponse()
        raw = response.read().decode()
        content_type = response.getheader("Content-Type", "")
        conn.close()
        if "application/json" in content_type:
            return response.status, json.loads(raw)
        return response.status, raw



def sample_driver(driver_id: str, lat: float, lon: float) -> Driver:
    return Driver(
        id=driver_id,
        status=DriverStatus.AVAILABLE,
        lat=lat,
        lon=lon,
        heading=0,
        speed_mps=10,
        last_update_ts=now_ms(),
        city_id="sf",
        idle_since_ts=1,
    )



def sample_request(request_id: str) -> RideRequest:
    return RideRequest(
        id=request_id,
        rider_id=f"r-{request_id}",
        created_ts=now_ms(),
        max_pickup_km=5,
        preferences=RidePreferences(quiet_mode=False, accessibility=False),
        city_id="sf",
        pickup_lat=37.775,
        pickup_lon=-122.418,
        dropoff_lat=37.785,
        dropoff_lon=-122.406,
    )



def test_healthz_ok(tmp_path: Path) -> None:
    with ServerHarness(tmp_path) as harness:
        status, payload = harness.request("GET", "/healthz")
    assert status == 200
    assert payload == {"ok": True}



def test_driver_upsert_and_world_snapshot(tmp_path: Path) -> None:
    with ServerHarness(tmp_path) as harness:
        driver = sample_driver("d-1", 37.775, -122.417)
        upsert_status, _ = harness.request("POST", "/driver", to_dict(driver))
        world_status, world_payload = harness.request("GET", "/world")

    assert upsert_status == 200
    assert world_status == 200
    assert isinstance(world_payload, dict)
    drivers = world_payload["drivers"]
    assert isinstance(drivers, list)
    assert any(d["id"] == "d-1" and d["status"] == "AVAILABLE" for d in drivers)



def test_request_ride_creates_match(tmp_path: Path) -> None:
    with ServerHarness(tmp_path) as harness:
        harness.request("POST", "/driver", to_dict(sample_driver("d-2", 37.7752, -122.4181)))
        ride_req = sample_request("req-http")
        status, match_payload = harness.request("POST", "/request-ride", to_dict(ride_req))
        events_status, events_payload = harness.request("GET", "/replay/events")

    assert status == 200
    assert isinstance(match_payload, dict)
    assert match_payload["driver_id"] == "d-2"
    assert match_payload["request_id"] == "req-http"

    assert events_status == 200
    assert isinstance(events_payload, dict)
    events = events_payload.get("events", [])
    assert isinstance(events, list)
    assert any(evt.get("type") == "MATCHED" for evt in events)



def test_metrics_and_traces_endpoints_exist(tmp_path: Path) -> None:
    with ServerHarness(tmp_path) as harness:
        harness.request("POST", "/driver", to_dict(sample_driver("d-3", 37.776, -122.417)))
        harness.request("POST", "/request-ride", to_dict(sample_request("req-metrics")))

        metrics_status, metrics_payload = harness.request("GET", "/metrics")
        traces_status, traces_payload = harness.request("GET", "/traces")

    assert metrics_status == 200
    assert isinstance(metrics_payload, str)
    assert "matches_total" in metrics_payload
    assert "match_latency_ms_p50" in metrics_payload

    assert traces_status == 200
    assert isinstance(traces_payload, dict)
    spans = traces_payload.get("spans")
    assert isinstance(spans, list)
