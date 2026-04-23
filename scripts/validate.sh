#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-fast}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "$MODE" != "fast" && "$MODE" != "full" ]]; then
  echo "Usage: ./scripts/validate.sh [fast|full]"
  exit 1
fi

if [[ -z "${TEST_EMAIL:-}" ]]; then
  export TEST_EMAIL="test@test.com"
fi
if [[ -z "${TEST_PASSWORD:-}" ]]; then
  export TEST_PASSWORD='$1MhDupRhDqzqGY'
fi

run_backend_pytest() {
  local target="$1"
  (
    cd "$ROOT_DIR/backend"
    if [[ ! -f "venv/bin/activate" ]]; then
      echo "backend/venv is missing. Create it before running validation."
      exit 1
    fi
    # shellcheck disable=SC1091
    source "venv/bin/activate"
    python -m pytest $target
  )
}

run_e2e_smoke() {
  (
    cd "$ROOT_DIR"
    node e2e/module1.mjs
  )
}

run_e2e_auth_chat() {
  local attempts=0
  local max_attempts=2

  until (( attempts >= max_attempts )); do
    attempts=$((attempts + 1))
    if (
      cd "$ROOT_DIR"
      TEST_EMAIL="$TEST_EMAIL" TEST_PASSWORD="$TEST_PASSWORD" node e2e/module1-auth-chat.mjs
    ); then
      return 0
    fi

    if (( attempts < max_attempts )); then
      echo "[validate] Auth+chat E2E failed; retrying ($attempts/$max_attempts)..."
    fi
  done

  echo "[validate] Auth+chat E2E failed after $max_attempts attempts"
  return 1
}

echo "[validate] Mode: $MODE"

echo "[validate] Layer A smoke"
run_e2e_smoke

if [[ "$MODE" == "fast" ]]; then
  echo "[validate] Layer B key unit tests"
  run_backend_pytest "tests/unit/test_chunking_service.py tests/unit/test_secret_crypto_service.py tests/unit/test_user_runtime_settings_service.py"

  echo "[validate] Layer C key integration checks"
  run_backend_pytest "tests/integration/test_api_contract.py::test_protected_threads_requires_auth"

  echo "[validate] Layer D auth+chat regression"
  run_e2e_auth_chat

  echo "[validate] Fast validation complete"
  exit 0
fi

echo "[validate] Layer B full unit"
run_backend_pytest "tests/unit"

echo "[validate] Layer C full integration"
run_backend_pytest "tests/integration"

echo "[validate] Layer D auth+chat regression"
run_e2e_auth_chat

echo "[validate] Full validation complete"
