#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PYTHONPATH="$ROOT/packages/protocol/src:$ROOT/packages/geo/src:$ROOT/apps/api/src:$ROOT/apps/simulator/src:${PYTHONPATH:-}"

python -m hyperdispatch_api.server &
API_PID=$!
python -m hyperdispatch_sim.runner --seed 1337 --drivers 20 --requests 30 --live &
SIM_PID=$!
python -m http.server 5173 --directory apps/web >/dev/null 2>&1 &
WEB_PID=$!

echo "HyperDispatch demo up: api=http://127.0.0.1:8000 web=http://127.0.0.1:5173"
cleanup(){
  kill $SIM_PID $API_PID $WEB_PID >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM
wait
