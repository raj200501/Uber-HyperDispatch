# Replay

Replay records dispatch events into SQLite.

## Flow
- start replay run metadata
- append every dispatch event
- stop replay
- rerun from the same seed/scenario
- produce diff (`expected_matches`, `observed_matches`, `match_delta`)

This gives deterministic reproducibility for debugging and interviews.
