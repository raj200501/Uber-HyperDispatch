from hyperdispatch_sim.scenarios import list_scenarios
from hyperdispatch_sim.sim import DeterministicSim


def test_deterministic_seed():
    left = DeterministicSim(seed=42, scenario="baseline_city").spawn_drivers(5)
    right = DeterministicSim(seed=42, scenario="baseline_city").spawn_drivers(5)
    assert left[0].lat == right[0].lat
    assert left[0].lon == right[0].lon


def test_scenario_request_generation():
    sim = DeterministicSim(seed=1, scenario="stadium_event")
    request = sim.request(3)
    assert request.id == "req-3"
    assert request.city_id == "sf"


def test_all_required_scenarios_exist():
    names = set(list_scenarios())
    required = {"baseline_city", "stadium_event", "airport_rush", "rain_surge", "downtown_gridlock", "chaos_monkey"}
    assert required.issubset(names)
