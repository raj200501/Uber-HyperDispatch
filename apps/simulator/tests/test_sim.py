from hyperdispatch_sim.sim import DeterministicSim


def test_deterministic_seed():
    left = DeterministicSim(seed=42).spawn_drivers(5)
    right = DeterministicSim(seed=42).spawn_drivers(5)
    assert left[0].lat == right[0].lat
    assert left[0].lon == right[0].lon


def test_scenario_request_generation():
    sim = DeterministicSim(seed=1)
    request = sim.request(3)
    assert request.id == "req-3"
    assert request.city_id == "sf"
