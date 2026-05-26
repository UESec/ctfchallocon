#!/usr/bin/env bash
set -euo pipefail

APP_HOME="/srv/orange-printer"
FLAG_FILE="/opt/orange-plant/orange_reactor_recipe.flag"

if [ ! -f "$FLAG_FILE" ]; then
  echo "[BOOT][ERROR] Flag file missing: $FLAG_FILE"
  exit 1
fi

echo "[BOOT] Starting internal Redis cache on 127.0.0.1:6379"

redis-server \
  --bind 127.0.0.1 \
  --port 6379 \
  --save "" \
  --appendonly no \
  --protected-mode no \
  --daemonize yes

echo "[BOOT] Waiting for Redis"

for i in $(seq 1 30); do
  if redis-cli -h 127.0.0.1 -p 6379 PING >/dev/null 2>&1; then
    break
  fi
  sleep 0.2
done

if ! redis-cli -h 127.0.0.1 -p 6379 PING >/dev/null 2>&1; then
  echo "[BOOT][ERROR] Redis did not start"
  exit 1
fi

echo "[BOOT] Loading Orange Power Plant recipe into Redis"

redis-cli -h 127.0.0.1 -p 6379 SET flag "$(cat "$FLAG_FILE")" >/dev/null
redis-cli -h 127.0.0.1 -p 6379 SET plant_status "ORANGE_REACTOR_DEGRADED_MODE" >/dev/null
redis-cli -h 127.0.0.1 -p 6379 SET backup_server_hint "The next incident moved to orange-backup-01. Operators used SSH for emergency maintenance." >/dev/null
redis-cli -h 127.0.0.1 -p 6379 SET backup_server "orange-backup-01:22" >/dev/null
redis-cli -h 127.0.0.1 -p 6379 SET incident_note "Reception printer diagnostics should never have been able to talk to local Redis." >/dev/null

echo "[BOOT] Starting Orange Plant Reception Printer"

cd "$APP_HOME"
exec bundle exec rackup config.ru -o 0.0.0.0 -p 4567
