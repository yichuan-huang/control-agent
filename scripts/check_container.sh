#!/usr/bin/env bash
set -euo pipefail

cd /app
case "${1:-}" in
  python)
    uv lock --check
    uv sync --locked
    rm -rf /app/build
    uv run --locked ruff format --check .
    uv run --locked ruff check .
    uv run --locked pytest -q
    uv run --locked pytest -q tests/test_main_cli.py
    ;;
  frontend)
    cd cfdc/web/frontend
    pnpm install --frozen-lockfile
    pnpm run format:check
    pnpm run typecheck
    pnpm run lint
    pnpm run test
    pnpm run build
    pnpm exec playwright install chromium
    pnpm run test:live-redaction
    pnpm run test:e2e
    ;;
  *)
    printf 'usage: %s python|frontend\n' "$0" >&2
    exit 2
    ;;
esac
