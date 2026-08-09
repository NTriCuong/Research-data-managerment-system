#!/usr/bin/env bash
set -euo pipefail

: "${ELASTIC_URL:?ELASTIC_URL is required}"
: "${ELASTIC_USERNAME:?ELASTIC_USERNAME is required}"
: "${ELASTIC_PASSWORD:?ELASTIC_PASSWORD is required}"
: "${KIBANA_PASSWORD:?KIBANA_PASSWORD is required}"
: "${RDMS_ELASTIC_PASSWORD:?RDMS_ELASTIC_PASSWORD is required}"
: "${ELASTIC_INDEX:?ELASTIC_INDEX is required}"
: "${ELASTIC_ALIAS:?ELASTIC_ALIAS is required}"
: "${ELASTIC_CA_CERT:?ELASTIC_CA_CERT is required}"

curl_es() {
    curl --silent --show-error --fail \
        --cacert "$ELASTIC_CA_CERT" \
        --user "$ELASTIC_USERNAME:$ELASTIC_PASSWORD" \
        "$@"
}

echo "Waiting for Elasticsearch"
until curl_es "$ELASTIC_URL/_cluster/health?wait_for_status=yellow&timeout=5s" >/dev/null; do
    sleep 5
done

curl_es \
    --request POST \
    --header "Content-Type: application/json" \
    --data "{\"password\":\"$KIBANA_PASSWORD\"}" \
    "$ELASTIC_URL/_security/user/kibana_system/_password" >/dev/null

curl_es \
    --request PUT \
    --header "Content-Type: application/json" \
    --data "{\"cluster\":[\"monitor\"],\"indices\":[{\"names\":[\"${ELASTIC_ALIAS}*\"],\"privileges\":[\"read\",\"write\",\"view_index_metadata\"]}]}" \
    "$ELASTIC_URL/_security/role/rdms_backend_role" >/dev/null

curl_es \
    --request PUT \
    --header "Content-Type: application/json" \
    --data "{\"password\":\"$RDMS_ELASTIC_PASSWORD\",\"roles\":[\"rdms_backend_role\"]}" \
    "$ELASTIC_URL/_security/user/rdms_backend" >/dev/null

if ! curl_es "$ELASTIC_URL/$ELASTIC_INDEX" >/dev/null 2>&1; then
    echo "Creating index $ELASTIC_INDEX"
    curl_es \
        --request PUT \
        --header "Content-Type: application/json" \
        --data-binary "@/opt/rdms/indices/rdms_research_objects_v1.json" \
        "$ELASTIC_URL/$ELASTIC_INDEX" >/dev/null
fi

echo "Ensuring alias $ELASTIC_ALIAS points to $ELASTIC_INDEX"
curl_es \
    --request POST \
    --header "Content-Type: application/json" \
    --data "{\"actions\":[{\"add\":{\"index\":\"$ELASTIC_INDEX\",\"alias\":\"$ELASTIC_ALIAS\",\"is_write_index\":true}}]}" \
    "$ELASTIC_URL/_aliases" >/dev/null

echo "Elasticsearch initialization completed"
