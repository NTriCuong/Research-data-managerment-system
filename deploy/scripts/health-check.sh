#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/../.." && pwd)"
env_file="${COMPOSE_ENV_FILE:-.env}"

cd "$project_root"
docker compose --env-file "$env_file" ps
docker compose --env-file "$env_file" exec -T backend curl --fail --silent http://localhost:8000/health
docker compose --env-file "$env_file" exec -T backend \
    sh -c 'curl --fail --silent --cacert "$ELASTIC_CA_CERT" --user "$ELASTIC_USERNAME:$ELASTIC_PASSWORD" "$ELASTIC_HOST/_cluster/health"'
