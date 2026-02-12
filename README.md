# uber-hyperdispatch / HyperDispatch

Real-time ride matching monorepo with FastAPI, SQLite WAL, custom geo grid index, simulator, and React ops dashboard.

## Quickstart
- `make bootstrap`
- `make verify`
- `make demo`

## Architecture

```
simulator -> API (REST) -> SQLite + GridIndex
                     -> WS /ws/world -> Web dashboard
```

## System design talking points
- Custom in-memory cell grid for low-latency candidate retrieval
- Per-driver async locks for atomic match assignment
- Snapshot streaming at 5Hz for smooth ops visibility

## Notes
- Zero API keys: OSM tiles via Leaflet.
- CI contract: `make verify`.
