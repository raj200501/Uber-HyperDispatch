from __future__ import annotations

import argparse
import time

from hyperdispatch_sim.scenarios import list_scenarios
from hyperdispatch_sim.sim import DeterministicSim


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--drivers", type=int, default=20)
    parser.add_argument("--requests", type=int, default=30)
    parser.add_argument("--scenario", type=str, default="baseline_city", choices=list_scenarios())
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    sim = DeterministicSim(args.seed, scenario=args.scenario)
    drivers = sim.spawn_drivers(args.drivers)
    print(f"seed={args.seed} scenario={args.scenario} drivers={len(drivers)}")
    req_idx = 0
    while True:
        req = sim.request(req_idx)
        print(f"request={req.id} pickup=({req.pickup_lat:.4f},{req.pickup_lon:.4f})")
        req_idx += 1
        if not args.live and req_idx >= args.requests:
            break
        time.sleep(0.2)


if __name__ == "__main__":
    main()
