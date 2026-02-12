# Uber HyperDispatch Control Tower

A deterministic dispatch simulation platform with a control-tower style UI, bounded geospatial indexing, replay/diff workflows, and CI-oriented verification.

## 60-second quickstart
1. `make bootstrap`
2. `make verify`
3. `make demo`
4. Open `http://127.0.0.1:5173`

## Commands
- `make bootstrap` — setup root venv and web deps
- `make verify` — python lint/tests (+ web checks when deps are present)
- `make demo` — run API + simulator + web
- `make loc` — line counts by area

## Interview talking points
- **Latency**: bounded candidate search with k-ring expansion and scan counters.
- **Indexing**: O(1) insert/update/remove in `GeoGridIndex`.
- **Replay**: deterministic replay and diff for confidence and regressions.
- **Determinism**: single seeded PRNG in simulator.
- **Backpressure-ready UI model**: separate world/events/traces streams.
