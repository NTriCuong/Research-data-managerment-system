#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <backup.dump>" >&2
    exit 2
fi

backup_file="$1"
if [[ ! -f "$backup_file" ]]; then
    echo "Backup file not found: $backup_file" >&2
    exit 2
fi

if [[ "${CONFIRM_RESTORE:-}" != "yes" ]]; then
    echo "Restore replaces objects in the target database." >&2
    echo "Run again with CONFIRM_RESTORE=yes after verifying the target environment." >&2
    exit 2
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/../.." && pwd)"
env_file="${COMPOSE_ENV_FILE:-.env}"

cd "$project_root"
docker compose --env-file "$env_file" exec -T postgres \
    sh -c 'exec pg_restore --clean --if-exists --no-owner --no-privileges --username="$POSTGRES_USER" --dbname="$POSTGRES_DB"' \
    < "$backup_file"

echo "Restore completed from: $backup_file"
