#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
project_root="$(cd -- "$script_dir/../.." && pwd)"
env_file="${ELASTIC_ADMIN_ENV_FILE:-.env.elasticsearch-admin}"

cd "$project_root"
if [[ ! -f "$env_file" ]]; then
    echo "Missing Elasticsearch admin environment file: $env_file" >&2
    exit 1
fi

set -a
# shellcheck disable=SC1090
source "$env_file"
set +a

: "${ELASTIC_ADMIN_URL:?ELASTIC_ADMIN_URL is required}"
: "${ELASTIC_ADMIN_USERNAME:?ELASTIC_ADMIN_USERNAME is required}"
: "${ELASTIC_ADMIN_PASSWORD:?ELASTIC_ADMIN_PASSWORD is required}"
: "${ELASTIC_ADMIN_CA_CERT:?ELASTIC_ADMIN_CA_CERT is required}"
: "${RDMS_ELASTIC_PASSWORD:?RDMS_ELASTIC_PASSWORD is required}"

ELASTIC_INDEX="${ELASTIC_INDEX:-rdms_research_objects_v1}"
ELASTIC_ALIAS="${ELASTIC_ALIAS:-rdms_research_objects}"
mapping_file="deploy/elasticsearch/indices/rdms_research_objects_v1.json"

curl_es() {
    curl --silent --show-error --fail-with-body \
        --ssl-revoke-best-effort \
        --cacert "$ELASTIC_ADMIN_CA_CERT" \
        --user "$ELASTIC_ADMIN_USERNAME:$ELASTIC_ADMIN_PASSWORD" \
        "$@"
}

curl_es \
    --request PUT \
    --header "Content-Type: application/json" \
    --data "{\"cluster\":[\"monitor\"],\"indices\":[{\"names\":[\"${ELASTIC_ALIAS}*\"],\"privileges\":[\"read\",\"write\",\"view_index_metadata\"]}]}" \
    "$ELASTIC_ADMIN_URL/_security/role/rdms_backend_role" >/dev/null

curl_es \
    --request PUT \
    --header "Content-Type: application/json" \
    --data "{\"password\":\"$RDMS_ELASTIC_PASSWORD\",\"roles\":[\"rdms_backend_role\"]}" \
    "$ELASTIC_ADMIN_URL/_security/user/rdms_backend" >/dev/null

if curl_es "$ELASTIC_ADMIN_URL/$ELASTIC_INDEX" >/dev/null 2>&1; then
    if ! curl_es "$ELASTIC_ADMIN_URL/$ELASTIC_INDEX/_settings" | grep -q 'rdms_english'; then
        echo "Index $ELASTIC_INDEX already exists without rdms_english." >&2
        echo "Create a new versioned index, reindex data, then switch the alias." >&2
        exit 1
    fi
else
    echo "Creating Elasticsearch index: $ELASTIC_INDEX"
    curl_es \
        --request PUT \
        --header "Content-Type: application/json" \
        --data-binary "@$mapping_file" \
        "$ELASTIC_ADMIN_URL/$ELASTIC_INDEX" >/dev/null
fi

curl_es \
    --request POST \
    --header "Content-Type: application/json" \
    --data "{\"actions\":[{\"add\":{\"index\":\"$ELASTIC_INDEX\",\"alias\":\"$ELASTIC_ALIAS\",\"is_write_index\":true}}]}" \
    "$ELASTIC_ADMIN_URL/_aliases" >/dev/null

echo "RDMS Elasticsearch user, role, index and alias are ready."
