#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/../.." && pwd)"
env_file="${COMPOSE_ENV_FILE:-.env}"
backup_dir="${BACKUP_DIR:-$project_root/deploy/backups}"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_file="$backup_dir/rdms-$timestamp.dump"

mkdir -p "$backup_dir"
cd "$project_root"

docker compose --env-file "$env_file" exec -T postgres \
    sh -c 'exec pg_dump --format=custom --no-password --username="$POSTGRES_USER" --dbname="$POSTGRES_DB"' \
    > "$backup_file"

echo "Backup created: $backup_file"
