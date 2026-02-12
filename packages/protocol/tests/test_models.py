from hyperdispatch_protocol import Driver, DriverStatus, RidePreferences, RideRequest, SimBounds, City, to_dict


def test_city_and_driver_serialization():
    city = City(id="sf", name="San Francisco", center_lat=37.7749, center_lon=-122.4194, sim_bounds=SimBounds(37.70, -122.52, 37.84, -122.35))
    driver = Driver(id="d1", status=DriverStatus.AVAILABLE, lat=37.77, lon=-122.41, heading=90, speed_mps=10, last_update_ts=1, city_id=city.id)
    request = RideRequest(
        id="req-1",
        rider_id="r1",
        created_ts=2,
        max_pickup_km=3,
        preferences=RidePreferences(quiet_mode=True),
        city_id=city.id,
        pickup_lat=37.76,
        pickup_lon=-122.41,
        dropoff_lat=37.78,
        dropoff_lon=-122.43,
    )
    payload = to_dict({"city": city, "driver": driver, "request": request})
    assert payload["city"]["name"] == "San Francisco"
    assert payload["driver"]["status"] == "AVAILABLE"
    assert payload["request"]["preferences"]["quiet_mode"] is True
