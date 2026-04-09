#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
RUN_DIR="$ROOT_DIR/.run"
LOG_DIR="$RUN_DIR/logs"
BACKEND_PID_FILE="$RUN_DIR/backend.pid"
FRONTEND_PID_FILE="$RUN_DIR/frontend.pid"

mkdir -p "$LOG_DIR"

backend_port=8000
frontend_port=5173

backend_url="http://127.0.0.1:${backend_port}/health"
frontend_url="http://localhost:${frontend_port}"

port_pid() {
  lsof -ti tcp:"$1" 2>/dev/null || true
}

is_pid_alive() {
  local pid="$1"
  kill -0 "$pid" 2>/dev/null
}

wait_for_http() {
  local url="$1"
  local name="$2"
  local retries=30
  local sleep_seconds=1

  for _ in $(seq 1 "$retries"); do
    if curl -fsS "$url" >/dev/null 2>&1; then
      echo "[ok] $name is ready: $url"
      return 0
    fi
    sleep "$sleep_seconds"
  done

  echo "[error] Timed out waiting for $name at $url"
  return 1
}

start_backend() {
  local port_holder
  port_holder="$(port_pid "$backend_port")"
  if [[ -n "$port_holder" ]]; then
    if curl -fsS "$backend_url" >/dev/null 2>&1; then
      echo "[info] Backend already healthy on port $backend_port."
      return 0
    fi
    echo "[warn] Backend port $backend_port is occupied but unhealthy. Reclaiming port."
    xargs kill 2>/dev/null <<<"$port_holder" || true
    sleep 1
  fi

  if [[ ! -d "$BACKEND_DIR/venv" ]]; then
    echo "[error] Missing backend virtual environment at $BACKEND_DIR/venv"
    echo "        Run: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
  fi

  echo "[info] Starting backend..."
  (
    cd "$BACKEND_DIR"
    source venv/bin/activate
    nohup uvicorn app.main:app --reload --host 127.0.0.1 --port "$backend_port" >"$LOG_DIR/backend.log" 2>&1 &
    echo $! >"$BACKEND_PID_FILE"
  )

  wait_for_http "$backend_url" "backend"
}

start_frontend() {
  local port_holder
  port_holder="$(port_pid "$frontend_port")"
  if [[ -n "$port_holder" ]]; then
    if curl -fsS "$frontend_url" >/dev/null 2>&1; then
      echo "[info] Frontend already reachable on port $frontend_port."
      return 0
    fi
    echo "[warn] Frontend port $frontend_port is occupied but unreachable. Reclaiming port."
    xargs kill 2>/dev/null <<<"$port_holder" || true
    sleep 1
  fi

  if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
    echo "[error] Missing frontend dependencies at $FRONTEND_DIR/node_modules"
    echo "        Run: cd frontend && npm install"
    exit 1
  fi

  echo "[info] Starting frontend..."
  (
    cd "$FRONTEND_DIR"
    nohup npm run dev -- --host 127.0.0.1 --port "$frontend_port" >"$LOG_DIR/frontend.log" 2>&1 &
    echo $! >"$FRONTEND_PID_FILE"
  )

  wait_for_http "$frontend_url" "frontend"
}

stop_from_pid_file() {
  local pid_file="$1"
  local name="$2"

  if [[ ! -f "$pid_file" ]]; then
    echo "[info] No $name pid file found."
    return 0
  fi

  local pid
  pid="$(cat "$pid_file")"

  if is_pid_alive "$pid"; then
    echo "[info] Stopping $name (pid: $pid)..."
    kill "$pid" 2>/dev/null || true
  else
    echo "[info] $name pid file exists but process is not running (pid: $pid)."
  fi

  rm -f "$pid_file"
}

stop_services() {
  stop_from_pid_file "$BACKEND_PID_FILE" "backend"
  stop_from_pid_file "$FRONTEND_PID_FILE" "frontend"

  local b_port_pid f_port_pid
  b_port_pid="$(port_pid "$backend_port")"
  f_port_pid="$(port_pid "$frontend_port")"

  if [[ -n "$b_port_pid" ]]; then
    echo "[info] Killing process on backend port $backend_port."
    xargs kill 2>/dev/null <<<"$b_port_pid" || true
  fi
  if [[ -n "$f_port_pid" ]]; then
    echo "[info] Killing process on frontend port $frontend_port."
    xargs kill 2>/dev/null <<<"$f_port_pid" || true
  fi

  echo "[ok] Services stopped."
}

status_services() {
  local b_port_pid f_port_pid
  b_port_pid="$(port_pid "$backend_port")"
  f_port_pid="$(port_pid "$frontend_port")"

  if [[ -n "$b_port_pid" ]]; then
    echo "[ok] Backend is running on :$backend_port (pid(s): $(echo "$b_port_pid" | tr '\n' ' '))"
  else
    echo "[info] Backend is not running on :$backend_port"
  fi

  if [[ -n "$f_port_pid" ]]; then
    echo "[ok] Frontend is running on :$frontend_port (pid(s): $(echo "$f_port_pid" | tr '\n' ' '))"
  else
    echo "[info] Frontend is not running on :$frontend_port"
  fi

  curl -fsS "$backend_url" >/dev/null 2>&1 && echo "[ok] Backend health endpoint reachable" || echo "[warn] Backend health endpoint not reachable"
  curl -fsS "$frontend_url" >/dev/null 2>&1 && echo "[ok] Frontend endpoint reachable" || echo "[warn] Frontend endpoint not reachable"
}

show_logs() {
  echo "== backend log =="
  tail -n 40 "$LOG_DIR/backend.log" 2>/dev/null || echo "(no backend log yet)"
  echo
  echo "== frontend log =="
  tail -n 40 "$LOG_DIR/frontend.log" 2>/dev/null || echo "(no frontend log yet)"
}

usage() {
  cat <<EOF
Usage: scripts/start-services.sh <command>

Commands:
  start   Start backend and frontend services
  stop    Stop backend and frontend services
  status  Show service and endpoint status
  logs    Show recent backend/frontend logs
  restart Stop then start services
EOF
}

main() {
  local cmd="${1:-}"

  case "$cmd" in
    start)
      start_backend
      start_frontend
      echo "[ok] Services started."
      echo "      Backend:  $backend_url"
      echo "      Frontend: $frontend_url"
      ;;
    stop)
      stop_services
      ;;
    status)
      status_services
      ;;
    logs)
      show_logs
      ;;
    restart)
      stop_services
      start_backend
      start_frontend
      echo "[ok] Services restarted."
      ;;
    *)
      usage
      exit 1
      ;;
  esac
}

main "$@"
