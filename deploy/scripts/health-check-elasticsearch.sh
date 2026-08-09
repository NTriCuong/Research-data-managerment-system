#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/../.." && pwd)"
env_file="${ELASTIC_COMPOSE_ENV_FILE:-.env.elasticsearch}"

cd "$project_root"
docker compose --env-file "$env_file" -f compose.elasticsearch.yaml ps
docker compose --env-file "$env_file" -f compose.elasticsearch.yaml exec -T elasticsearch \
    sh -c 'curl --fail --silent --cacert config/certs/ca/ca.crt --user "elastic:$ELASTIC_PASSWORD" https://localhost:9200/_cluster/health'
