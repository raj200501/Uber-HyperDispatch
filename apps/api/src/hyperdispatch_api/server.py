from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from hyperdispatch_api.main import app


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        if parsed.path == "/healthz":
            self._send(200, app.healthz())
            return
        if parsed.path == "/readyz":
            self._send(200, app.readyz())
            return
        if parsed.path == "/world":
            self._send(200, app.world())
            return
        if parsed.path == "/metrics":
            payload = app.metrics().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if parsed.path == "/replay/runs":
            self._send(200, {"runs": app.replay_runs()})
            return
        if parsed.path == "/replay/events":
            from_ts = int(query.get("from_ts", [0])[0])
            run_id = query.get("run_id", [None])[0]
            self._send(200, {"events": app.replay_events(run_id=run_id, from_ts=from_ts)})
            return
        if parsed.path == "/traces":
            self._send(200, {"spans": app.traces()})
            return
        self._send(404, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)
        body = self._read_body()

        if parsed.path == "/driver":
            self._send(200, app.upsert_driver(body))
            return
        if parsed.path == "/request-ride":
            self._send(200, app.request_ride(body))
            return
        if parsed.path == "/replay/start":
            seed = int(query.get("seed", [1337])[0])
            scenario = query.get("scenario", ["baseline_city"])[0]
            city_id = query.get("city_id", ["sf"])[0]
            self._send(200, app.replay_start(seed=seed, scenario=scenario, city_id=city_id))
            return
        if parsed.path == "/replay/stop":
            run_id = query.get("run_id", [None])[0]
            self._send(200, app.replay_stop(run_id=run_id))
            return
        if parsed.path == "/replay/rerun":
            run_id = query.get("run_id", [None])[0]
            if not run_id:
                self._send(400, {"error": "run_id_required"})
                return
            self._send(200, app.replay_rerun(run_id))
            return
        self._send(404, {"error": "not_found"})

    def _read_body(self) -> dict[str, object]:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length <= 0:
            return {}
        raw = self.rfile.read(content_length)
        return json.loads(raw.decode())

    def _send(self, code: int, body: dict[str, object]) -> None:
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
