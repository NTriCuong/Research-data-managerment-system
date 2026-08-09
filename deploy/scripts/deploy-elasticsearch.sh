#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/../.." && pwd)"
env_file="${ELASTIC_COMPOSE_ENV_FILE:-.env.elasticsearch}"
compose_file="compose.elasticsearch.yaml"

cd "$project_root"

docker compose --env-file "$env_file" -f "$compose_file" config --quiet
docker compose --env-file "$env_file" -f "$compose_file" pull
docker compose --env-file "$env_file" -f "$compose_file" up --detach --remove-orphans
docker compose --env-file "$env_file" -f "$compose_file" ps
