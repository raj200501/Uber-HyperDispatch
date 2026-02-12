from hyperdispatch_geo.grid import GridIndex


def test_find_nearest_returns_sorted():
    grid = GridIndex(200)
    grid.upsert_driver("a", 37.77, -122.41)
    grid.upsert_driver("b", 37.78, -122.42)
    nearest = grid.find_nearest(37.77, -122.41, radius_km=5, limit=2)
    assert nearest[0][0] == "a"


def test_index_does_not_scan_every_driver(monkeypatch):
    grid = GridIndex(100)
    for i in range(2000):
        grid.upsert_driver(f"d{i}", 37.0 + (i % 50) * 0.01, -122.0 + (i // 50) * 0.01)

    calls = {"n": 0}
    from hyperdispatch_geo import grid as grid_mod

    original = grid_mod.haversine_m

    def wrapped(*args, **kwargs):
        calls["n"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(grid_mod, "haversine_m", wrapped)
    grid.find_nearest(37.77, -122.41, radius_km=1, limit=5)
    assert calls["n"] < 200
