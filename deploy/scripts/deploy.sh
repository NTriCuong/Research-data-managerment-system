#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/../.." && pwd)"
env_file="${COMPOSE_ENV_FILE:-.env}"

cd "$project_root"

docker compose --env-file "$env_file" config --quiet
docker compose --env-file "$env_file" pull --ignore-buildable
docker compose --env-file "$env_file" build --pull
docker compose --env-file "$env_file" up --detach --remove-orphans
docker compose --env-file "$env_file" ps
