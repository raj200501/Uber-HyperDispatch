from hyperdispatch_geo import GeoGridIndex


def test_query_returns_sorted_by_distance():
    index = GeoGridIndex(cell_km=0.2)
    index.insert_or_update("a", 37.77, -122.41)
    index.insert_or_update("b", 37.79, -122.43)
    ranked = index.query(37.77, -122.41, radius_km=5, limit=2)
    assert ranked[0][0] == "a"


def test_bounded_scan_does_not_touch_all_points():
    index = GeoGridIndex(cell_km=0.5)
    for i in range(2000):
        lat = 35.0 + (i % 100) * 0.05
        lon = -120.0 + (i // 100) * 0.05
        index.insert_or_update(f"d-{i}", lat, lon)

    _ = index.query(37.77, -122.41, radius_km=1.0, limit=8)
    assert index.index_points_scanned < 2000
    assert index.cells_visited < 300
