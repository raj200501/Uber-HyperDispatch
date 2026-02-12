# Matching Pipeline

1. **Validate + rider lock**: reject duplicate in-flight request IDs.
2. **Candidate fetch**: use `GeoGridIndex.query` with bounded radius and ring expansion.
3. **Filter**: only AVAILABLE and fresh drivers within staleness TTL.
4. **Score**:
   - distance term
   - ETA term
   - fairness term (idle time)
5. **Atomic claim**: lock driver, transition status to ENROUTE, emit MATCHED event.

Trace spans are persisted for each stage with timings and tags.
