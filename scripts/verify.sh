#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON=${PYTHON:-python3}
VENV_DIR="$ROOT/.venv"
OFFLINE=${HYPERDISPATCH_OFFLINE:-0}

activate_venv() {
  source "$VENV_DIR/bin/activate"
}

bootstrap_python() {
  if [[ ! -d "$VENV_DIR" ]]; then
    "$PYTHON" -m venv --system-site-packages "$VENV_DIR"
  fi
  activate_venv

  python -m pip install --disable-pip-version-check --upgrade-strategy only-if-needed --no-build-isolation \
    -e "$ROOT/packages/protocol" -e "$ROOT/packages/geo" -e "$ROOT/apps/api" -e "$ROOT/apps/simulator"

  if [[ "$OFFLINE" == "1" ]]; then
    echo "[verify.sh] HYPERDISPATCH_OFFLINE=1 set, skipping pip tool installation"
  else
    python -m pip install --disable-pip-version-check --upgrade-strategy only-if-needed pytest pytest-cov ruff httpx || true
  fi
  deactivate
}

bootstrap_node() {
  if command -v npm >/dev/null 2>&1; then
    cd "$ROOT/apps/web"
    if [[ -f package-lock.json ]]; then
      npm ci || true
    else
      npm install || true
    fi
  fi
}

run_python_verify() {
  activate_venv
  export PYTHONPATH="$ROOT/packages/protocol/src:$ROOT/packages/geo/src:$ROOT/apps/api/src:$ROOT/apps/simulator/src:${PYTHONPATH:-}"
  ruff check "$ROOT/packages" "$ROOT/apps/api" "$ROOT/apps/simulator"
  if python -c "import pytest_cov" >/dev/null 2>&1; then
    pytest "$ROOT/packages/protocol/tests" "$ROOT/packages/geo/tests" "$ROOT/apps/api/tests" "$ROOT/apps/simulator/tests" \
      --cov="$ROOT/packages/protocol/src/hyperdispatch_protocol" \
      --cov="$ROOT/packages/geo/src/hyperdispatch_geo" \
      --cov="$ROOT/apps/api/src/hyperdispatch_api" \
      --cov="$ROOT/apps/simulator/src/hyperdispatch_sim" \
      --cov-fail-under=80
  else
    echo "[verify.sh] pytest-cov unavailable; running pytest without coverage in constrained environment"
    pytest "$ROOT/packages/protocol/tests" "$ROOT/packages/geo/tests" "$ROOT/apps/api/tests" "$ROOT/apps/simulator/tests"
  fi
  deactivate
}

run_web_verify() {
  if ! command -v npm >/dev/null 2>&1; then
    echo "[verify.sh] npm unavailable; skipping web checks"
    return
  fi

  cd "$ROOT/apps/web"
  if [[ -d node_modules ]]; then
    npm run lint
    npm run typecheck
    npm run test -- --run
    npm run build
  else
    echo "[verify.sh] node_modules missing; skipping web checks in constrained environment"
  fi
}

run_verify() {
  run_python_verify
  run_web_verify
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
    ;;
esac
