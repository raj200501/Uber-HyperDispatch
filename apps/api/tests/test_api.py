from fastapi.testclient import TestClient
from hyperdispatch_protocol import Driver, DriverStatus, LatLng, MatchRequest

from hyperdispatch_api.main import app


client = TestClient(app)


def test_healthz():
    assert client.get("/healthz").status_code == 200


def test_match_flow():
    d = Driver(id="d1", location=LatLng(lat=37.77, lng=-122.41), heading_deg=0, speed_mps=8, status=DriverStatus.AVAILABLE, last_update_ms=1)
    client.post("/api/driver/d1/location", json=d.model_dump())
    req = MatchRequest(rider_id="r1", pickup=LatLng(lat=37.7701, lng=-122.4101), dropoff=LatLng(lat=37.78, lng=-122.42), constraints={})
    resp = client.post("/api/request-ride", json=req.model_dump())
    assert resp.status_code == 200
    body = resp.json()
    assert body["driver_id"] == "d1"
