from __future__ import annotations

import argparse
import time

import httpx

from .sim import DeterministicSim


def run(base_url: str, drivers: int, riders: int, seed: int = 1337) -> None:
    sim = DeterministicSim(seed)
    client = httpx.Client(base_url=base_url, timeout=5.0)
    client.post("/api/sim/reset")
    for d in sim.spawn_drivers(drivers):
        client.post(f"/api/driver/{d.id}/location", json=d.model_dump())
    i = 0
    while True:
        req = sim.random_request(i % max(riders, 1))
        client.post("/api/request-ride", json=req.model_dump())
        i += 1
        time.sleep(0.2)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://127.0.0.1:8000")
    p.add_argument("--drivers", type=int, default=20)
    p.add_argument("--riders", type=int, default=10)
    p.add_argument("--seed", type=int, default=1337)
    args = p.parse_args()
    run(args.base_url, args.drivers, args.riders, args.seed)
