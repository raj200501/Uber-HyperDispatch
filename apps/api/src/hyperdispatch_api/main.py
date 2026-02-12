from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from hyperdispatch_protocol import Driver, MatchRequest

from .engine import DispatchEngine

app = FastAPI(title="HyperDispatch API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
engine = DispatchEngine(Path(".hyperdispatch/hyperdispatch.db"))


@app.on_event("startup")
async def startup() -> None:
    async def broadcaster() -> None:
        while True:
            if engine.ws_clients:
                payload = engine.snapshot().model_dump_json()
                dead = []
                for ws in engine.ws_clients:
                    try:
                        await ws.send_text(payload)
                    except Exception:
                        dead.append(ws)
                for ws in dead:
                    engine.ws_clients.discard(ws)
            await asyncio.sleep(0.2)

    asyncio.create_task(broadcaster())


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/api/world")
def world():
    return engine.snapshot()


@app.websocket("/ws/world")
async def ws_world(ws: WebSocket):
    await ws.accept()
    engine.ws_clients.add(ws)
    try:
        while True:
            await ws.receive_text()
    except Exception:
        engine.ws_clients.discard(ws)


@app.post("/api/request-ride")
async def request_ride(req: MatchRequest):
    try:
        return await engine.request_ride(req)
    except ValueError as e:
        raise HTTPException(409, str(e)) from e


@app.post("/api/driver/{driver_id}/location")
def driver_location(driver_id: str, driver: Driver):
    if driver_id != driver.id:
        raise HTTPException(400, "id mismatch")
    engine.upsert_driver(driver)
    return {"ok": True}


@app.post("/api/rider/{rider_id}/location")
def rider_location(rider_id: str, payload: dict):
    return {"ok": True, "id": rider_id, "payload": payload}


@app.post("/api/sim/reset")
def reset():
    engine.db.reset()
    engine.grid = engine.grid.__class__(300)
    return {"ok": True}


@app.get("/api/trips")
def trips():
    return engine.list_trips()


@app.get("/api/trips/{trip_id}")
def trip(trip_id: str):
    matches = [t for t in engine.list_trips() if t.id == trip_id]
    if not matches:
        raise HTTPException(404)
    return matches[0]


@app.get("/api/traces/{trace_id}")
def traces(trace_id: str):
    return engine.trace(trace_id)


@app.get("/api/metrics")
def metrics():
    return engine.metrics()
