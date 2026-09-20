#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then echo "Usage: $0 <backup.dump>" >&2; exit 2; fi
BACKUP_FILE="$1"
COMPOSE_FILE="${COMPOSE_FILE:-QCSTS/docker/docker-compose.production.yml}"
test -f "$BACKUP_FILE"
docker compose -f "$COMPOSE_FILE" exec -T db pg_restore -U "${POSTGRES_USER:?POSTGRES_USER is required}" -d "${POSTGRES_DB:?POSTGRES_DB is required}" --clean --if-exists --no-owner --no-acl < "$BACKUP_FILE"
docker compose -f "$COMPOSE_FILE" exec -T db psql -U "${POSTGRES_USER:?POSTGRES_USER is required}" -d "${POSTGRES_DB:?POSTGRES_DB is required}" -c "SELECT current_database(), current_timestamp;"
