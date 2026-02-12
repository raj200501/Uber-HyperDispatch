from hyperdispatch_protocol import Driver, DriverStatus, LatLng


def test_driver_model():
    d = Driver(
        id="d1",
        location=LatLng(lat=1, lng=2),
        heading_deg=90,
        speed_mps=5,
        status=DriverStatus.AVAILABLE,
        last_update_ms=1,
    )
    assert d.location.lat == 1
