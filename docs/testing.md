# Testing

## Commands
- `make bootstrap`
- `make verify`
- `make demo`
- `make loc`

## Included checks
- Python: ruff + pytest + coverage (>=80)
- Web: lint, typecheck, vitest, build (when `node_modules` are available)
- Demo smoke: API/simulator/web startup script
