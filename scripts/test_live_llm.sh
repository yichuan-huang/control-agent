#!/usr/bin/env bash
# Host-side Docker orchestration only; clients and validation run in containers.
set -euo pipefail

mode="${1:-all}"
if [[ $# -gt 1 || ! "$mode" =~ ^(service|browser|all)$ ]]; then
  echo 'usage: bash scripts/test_live_llm.sh [service|browser|all]' >&2
  exit 2
fi
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
if [[ ! -e .env ]]; then
  (
    umask 077
    set -o noclobber
    printf 'CFDC_LLM_BASE_URL=\nCFDC_LLM_MODEL=\nCFDC_LLM_API_KEY=\n' > .env
  )
  echo 'Created .env (600). Please fill its three fields in your local editor, then rerun. Do not share the key in chat.' >&2
  exit 2
fi

# Compose, not the shell, parses the file. Same-name host values must not win.
unset CFDC_LLM_BASE_URL CFDC_LLM_MODEL CFDC_LLM_API_KEY
compose=(docker compose --project-directory "$root" -f "$root/compose.yaml" --env-file "$root/.env" --profile checks)
# Parser diagnostics can contain input values; never display them for a real file.
if ! "${compose[@]}" config --quiet >/dev/null 2>&1; then
  echo 'Cannot load the Compose configuration or .env. Check Docker and local file syntax without sharing credentials.' >&2
  exit 2
fi
service=frontend-check
if [[ "$mode" == service ]]; then
  service=python-check
fi
exec "${compose[@]}" run --build --rm -T \
  -e CFDC_LLM_BASE_URL -e CFDC_LLM_MODEL -e CFDC_LLM_API_KEY \
  -e CFDC_RUN_LIVE_LLM=1 \
  "$service" python /app/scripts/run_live_llm.py "$mode"
