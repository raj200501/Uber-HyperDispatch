#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON=${PYTHON:-python3}

bootstrap_python() {
  for dir in packages/protocol packages/geo apps/api apps/simulator; do
    "$PYTHON" -m venv "$dir/.venv"
    source "$dir/.venv/bin/activate"
    pip install -U pip >/dev/null
    pip install -e "$ROOT/packages/protocol" -e "$ROOT/packages/geo" >/dev/null
    if [[ "$dir" == "apps/api" || "$dir" == "apps/simulator" ]]; then
      pip install -e "$ROOT/$dir" >/dev/null
    fi
    pip install pytest pytest-cov ruff httpx >/dev/null
    deactivate
  done
}

bootstrap_node() {
  cd "$ROOT/apps/web"
  npm ci
}

run_verify() {
  source "$ROOT/apps/api/.venv/bin/activate"
  ruff check "$ROOT/packages" "$ROOT/apps/api" "$ROOT/apps/simulator"
  pytest "$ROOT/packages/protocol/tests" "$ROOT/packages/geo/tests" "$ROOT/apps/api/tests" "$ROOT/apps/simulator/tests" \
    --cov="$ROOT/packages/protocol/src/hyperdispatch_protocol" \
    --cov="$ROOT/packages/geo/src/hyperdispatch_geo" \
    --cov="$ROOT/apps/api/src/hyperdispatch_api" \
    --cov="$ROOT/apps/simulator/src/hyperdispatch_sim" \
    --cov-fail-under=80
  deactivate

  cd "$ROOT/apps/web"
  npm run lint
  npm run typecheck
  npm run test -- --run
  npm run build
}

case "${1:-verify}" in
  bootstrap)
    bootstrap_python
    bootstrap_node
    ;;
  verify)
    run_verify
    ;;
  *)
    echo "usage: $0 [bootstrap|verify]"
    exit 1
esac
