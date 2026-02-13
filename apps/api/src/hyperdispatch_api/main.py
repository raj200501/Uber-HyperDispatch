from __future__ import annotations

from pathlib import Path

from hyperdispatch_protocol import Driver, DriverStatus, RidePreferences, RideRequest, to_dict

from .engine import DispatchEngine
from .repository import DispatchRepository


class HyperDispatchApp:
    def __init__(self, db_path: Path | str = ":memory:"):
        self.repo = DispatchRepository(db_path)
        self.engine = DispatchEngine(self.repo)

    def healthz(self) -> dict[str, bool]:
        return {"ok": True}

    def readyz(self) -> dict[str, bool]:
        return {"ready": True}

    def world(self) -> dict[str, object]:
        return to_dict(self.engine.world())

    def upsert_driver(self, payload: dict[str, object]) -> dict[str, str]:
        normalized = dict(payload)
        status = normalized.get("status")
        if isinstance(status, str):
            normalized["status"] = DriverStatus(status)
        driver = Driver(**normalized)
        self.engine.add_driver(driver)
        return {"status": "ok"}

    def request_ride(self, payload: dict[str, object]) -> dict[str, object]:
        prefs_payload = payload.get("preferences") or {}
        payload = {**payload, "preferences": RidePreferences(**prefs_payload)}
        request = RideRequest(**payload)
        return to_dict(self.engine.match_request(request))

    def replay_start(self, seed: int, scenario: str, city_id: str) -> dict[str, str]:
        return {"run_id": self.engine.replay_start(seed=seed, scenario=scenario, city_id=city_id)}

    def replay_stop(self, run_id: str | None = None) -> dict[str, str]:
        return {"run_id": self.engine.replay_stop(run_id=run_id)}

    def replay_runs(self) -> list[dict[str, object]]:
        return self.engine.replay_runs()

    def replay_events(self, run_id: str | None = None, from_ts: int = 0) -> list[dict[str, object]]:
        return [to_dict(evt) for evt in self.engine.replay_events(run_id=run_id, from_ts=from_ts)]

    def replay_rerun(self, run_id: str) -> dict[str, object]:
        return self.engine.replay_run(run_id)

    def traces(self) -> list[dict[str, object]]:
        return [to_dict(span) for span in self.repo.list_spans()]

    def metrics(self) -> str:
        return self.engine.metrics_text()


app = HyperDispatchApp(Path(".hyperdispatch.db"))
