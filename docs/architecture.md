# HyperDispatch Architecture

```mermaid
flowchart LR
  SIM[Deterministic Simulator] --> API[Dispatch API]
  API --> GRID[GeoGridIndex]
  API --> DB[(SQLite WAL)]
  API --> WS1[/ws/world 5Hz/]
  API --> WS2[/ws/events/]
  API --> WS3[/ws/traces/]
  WS1 --> WEB[Control Tower Web]
  WS2 --> WEB
  WS3 --> WEB
```

## Core ideas
- Grid-indexed candidate retrieval (k-ring expansion) to avoid global scans.
- Multi-stage matching pipeline with traces at each stage.
- Replay and diff for deterministic verification of dispatch outcomes.
