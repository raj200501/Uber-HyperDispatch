#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

source apps/api/.venv/bin/activate
uvicorn hyperdispatch_api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!
deactivate

source apps/simulator/.venv/bin/activate
python -m hyperdispatch_sim.runner --base-url http://127.0.0.1:8000 --drivers 20 --riders 10 &
SIM_PID=$!
deactivate

cd apps/web
npm run dev -- --host 0.0.0.0 --port 5173 &
WEB_PID=$!

cleanup(){
  kill $SIM_PID $API_PID $WEB_PID >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM
wait
