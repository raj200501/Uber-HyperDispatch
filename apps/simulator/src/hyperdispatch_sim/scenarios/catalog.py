from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    name: str
    demand_rate: float
    speed_factor: float
    hotspot_bias: float
    chaos: bool = False


_SCENARIOS = {
    "baseline_city": Scenario("baseline_city", demand_rate=1.0, speed_factor=1.0, hotspot_bias=0.2),
    "stadium_event": Scenario("stadium_event", demand_rate=2.1, speed_factor=0.9, hotspot_bias=0.8),
    "airport_rush": Scenario("airport_rush", demand_rate=1.4, speed_factor=1.1, hotspot_bias=0.65),
    "rain_surge": Scenario("rain_surge", demand_rate=2.5, speed_factor=0.75, hotspot_bias=0.45),
    "downtown_gridlock": Scenario("downtown_gridlock", demand_rate=1.2, speed_factor=0.55, hotspot_bias=0.55),
    "chaos_monkey": Scenario("chaos_monkey", demand_rate=1.6, speed_factor=0.85, hotspot_bias=0.5, chaos=True),
}


def get_scenario(name: str) -> Scenario:
    return _SCENARIOS.get(name, _SCENARIOS["baseline_city"])


def list_scenarios() -> list[str]:
    return sorted(_SCENARIOS)
