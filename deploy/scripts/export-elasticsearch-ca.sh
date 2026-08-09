#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/../.." && pwd)"
env_file="${ELASTIC_COMPOSE_ENV_FILE:-.env.elasticsearch}"
output_file="${1:-$project_root/deploy/elasticsearch/certs/ca.crt}"
temporary_file="${output_file}.tmp"

mkdir -p "$(dirname -- "$output_file")"
cd "$project_root"

docker compose --env-file "$env_file" -f compose.elasticsearch.yaml \
    run --rm --no-deps --entrypoint cat elasticsearch-setup \
    /usr/share/elasticsearch/config/certs/ca/ca.crt > "$temporary_file"

mv "$temporary_file" "$output_file"
chmod 644 "$output_file"
echo "Elasticsearch CA exported to: $output_file"
