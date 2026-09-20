#!/usr/bin/env bash
set -euo pipefail
COMPOSE_FILE="${COMPOSE_FILE:-QCSTS/docker/docker-compose.production.yml}"
BACKUP_DIR="${BACKUP_DIR:-QCSTS/backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_DIR"
docker compose -f "$COMPOSE_FILE" exec -T db pg_dump -U "${POSTGRES_USER:?POSTGRES_USER is required}" -d "${POSTGRES_DB:?POSTGRES_DB is required}" --format=custom --no-owner --no-acl > "$BACKUP_DIR/qcsts-$STAMP.dump"
echo "Backup created: $BACKUP_DIR/qcsts-$STAMP.dump"
