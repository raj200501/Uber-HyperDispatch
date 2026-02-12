from hyperdispatch_sim.sim import DeterministicSim


def test_deterministic_seed():
    a = DeterministicSim(1337).spawn_drivers(3)
    b = DeterministicSim(1337).spawn_drivers(3)
    assert a[0].location == b[0].location
