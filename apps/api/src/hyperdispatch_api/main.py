from __future__ import annotations

from pathlib import Path

from hyperdispatch_protocol import Driver, to_dict

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

    def upsert_driver(self, driver: Driver) -> dict[str, str]:
        self.engine.add_driver(driver)
        return {"status": "ok"}

    def request_ride(self, request):
        return to_dict(self.engine.match_request(request))

    def metrics(self) -> str:
        return self.engine.metrics_text()


app = HyperDispatchApp(Path(".hyperdispatch.db"))
