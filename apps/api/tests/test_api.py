import threading
import time

from hyperdispatch_protocol import Driver, DriverStatus, to_dict

from hyperdispatch_api.main import HyperDispatchApp


def now_ms() -> int:
    return time.time_ns() // 1_000_000


def sample_driver(driver_id: str, lat: float, lon: float) -> Driver:
    return Driver(
        id=driver_id,
        status=DriverStatus.AVAILABLE,
        lat=lat,
        lon=lon,
        heading=0,
        speed_mps=9,
        last_update_ts=now_ms(),
        city_id="sf",
        idle_since_ts=1,
    )


def sample_request(request_id: str = "req-1") -> dict[str, object]:
    return {
        "id": request_id,
        "rider_id": f"r-{request_id}",
        "created_ts": now_ms(),
        "max_pickup_km": 4,
        "preferences": {"quiet_mode": False, "accessibility": False},
        "city_id": "sf",
        "pickup_lat": 37.775,
        "pickup_lon": -122.418,
        "dropoff_lat": 37.785,
        "dropoff_lon": -122.406,
    }


def test_health_and_ready():
    app = HyperDispatchApp(":memory:")
    assert app.healthz()["ok"] is True
    assert app.readyz()["ready"] is True


def test_matching_pipeline_and_metrics_and_world():
    app = HyperDispatchApp(":memory:")
    app.upsert_driver(to_dict(sample_driver("d1", 37.775, -122.417)))
    decision = app.request_ride(sample_request())
    assert decision["driver_id"] == "d1"
    assert "matches_total" in app.metrics()
    world = app.world()
    assert world["drivers"]
    assert world["requests"]


def test_replay_start_stop_events_rerun():
    app = HyperDispatchApp(":memory:")
    app.upsert_driver(to_dict(sample_driver("d2", 37.775, -122.417)))
    run = app.replay_start(seed=1337, scenario="baseline_city", city_id="sf")
    app.request_ride(sample_request("req-2"))
    app.replay_stop(run["run_id"])
    runs = app.replay_runs()
    assert runs and runs[0]["id"] == run["run_id"]
    events = app.replay_events(run_id=run["run_id"])
    assert events
    diff = app.replay_rerun(run["run_id"])
    assert diff["mismatch_count"] == 0


def test_contention_retries_next_driver():
    app = HyperDispatchApp(":memory:")
    app.upsert_driver(to_dict(sample_driver("busy", 37.775, -122.417)))
    app.upsert_driver(to_dict(sample_driver("free", 37.776, -122.418)))
    lock = app.engine.driver_locks.setdefault("busy", threading.Lock())
    lock.acquire()
    try:
        decision = app.request_ride(sample_request("req-3"))
        assert decision["driver_id"] == "free"
    finally:
        lock.release()


def test_metrics_shape_contains_index_counters():
    app = HyperDispatchApp(":memory:")
    app.upsert_driver(to_dict(sample_driver("d3", 37.775, -122.417)))
    app.request_ride(sample_request("req-4"))
    text = app.metrics()
    assert "index_cells_visited_avg" in text
    assert "index_points_scanned_avg" in text
