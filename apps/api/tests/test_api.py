import threading
import time

from hyperdispatch_protocol import Driver, DriverStatus, RidePreferences, RideRequest

from hyperdispatch_api.main import HyperDispatchApp


def now_ms() -> int:
    return time.time_ns() // 1_000_000


def make_request(request_id: str = "req-1") -> RideRequest:
    return RideRequest(
        id=request_id,
        rider_id=f"r-{request_id}",
        created_ts=now_ms(),
        max_pickup_km=4,
        preferences=RidePreferences(),
        city_id="sf",
        pickup_lat=37.775,
        pickup_lon=-122.418,
        dropoff_lat=37.785,
        dropoff_lon=-122.406,
    )


def test_health_and_ready():
    app = HyperDispatchApp(":memory:")
    assert app.healthz()["ok"] is True
    assert app.readyz()["ready"] is True


def test_matching_pipeline_and_metrics():
    app = HyperDispatchApp(":memory:")
    app.upsert_driver(
        Driver(
            id="d1",
            status=DriverStatus.AVAILABLE,
            lat=37.775,
            lon=-122.417,
            heading=0,
            speed_mps=8,
            last_update_ts=now_ms(),
            city_id="sf",
            idle_since_ts=1,
        )
    )
    decision = app.request_ride(make_request())
    assert decision["driver_id"] == "d1"
    assert "matches_total" in app.metrics()


def test_replay_and_diff():
    app = HyperDispatchApp(":memory:")
    app.upsert_driver(
        Driver(
            id="d2",
            status=DriverStatus.AVAILABLE,
            lat=37.775,
            lon=-122.417,
            heading=0,
            speed_mps=10,
            last_update_ts=now_ms(),
            city_id="sf",
            idle_since_ts=1,
        )
    )
    app.request_ride(make_request("req-2"))
    result = app.engine.replay_run()
    assert result["expected_matches"] == result["observed_matches"]


def test_contention_retries_next_driver():
    app = HyperDispatchApp(":memory:")
    app.upsert_driver(
        Driver(
            id="busy",
            status=DriverStatus.AVAILABLE,
            lat=37.775,
            lon=-122.417,
            heading=0,
            speed_mps=8,
            last_update_ts=now_ms(),
            city_id="sf",
            idle_since_ts=1,
        )
    )
    app.upsert_driver(
        Driver(
            id="free",
            status=DriverStatus.AVAILABLE,
            lat=37.776,
            lon=-122.418,
            heading=0,
            speed_mps=8,
            last_update_ts=now_ms(),
            city_id="sf",
            idle_since_ts=1,
        )
    )
    lock = app.engine.driver_locks.setdefault("busy", threading.Lock())
    lock.acquire()
    try:
        decision = app.request_ride(make_request("req-3"))
        assert decision["driver_id"] == "free"
    finally:
        lock.release()
