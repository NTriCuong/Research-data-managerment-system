#!/usr/bin/env bash
set -euo pipefail

cd /usr/share/elasticsearch

: "${ELASTIC_CERT_DNS:?ELASTIC_CERT_DNS is required}"
: "${ELASTIC_CERT_IP:?ELASTIC_CERT_IP is required}"

if [[ ! -f config/certs/ca/ca.crt ]]; then
    echo "Creating Elasticsearch certificate authority"
    bin/elasticsearch-certutil ca --silent --pem -out config/certs/ca.zip
    unzip -q config/certs/ca.zip -d config/certs
fi

if [[ ! -f config/certs/elasticsearch/elasticsearch.crt ]]; then
    echo "Creating Elasticsearch node certificate"
    cat > config/certs/instances.yml <<EOF
instances:
  - name: elasticsearch
    dns:
      - elasticsearch
      - localhost
EOF
    if [[ "${ELASTIC_CERT_DNS}" != "elasticsearch" && "${ELASTIC_CERT_DNS}" != "localhost" ]]; then
        printf '      - %s\n' "${ELASTIC_CERT_DNS}" >> config/certs/instances.yml
    fi
    cat >> config/certs/instances.yml <<EOF
    ip:
      - 127.0.0.1
EOF
    if [[ "${ELASTIC_CERT_IP}" != "127.0.0.1" ]]; then
        printf '      - %s\n' "${ELASTIC_CERT_IP}" >> config/certs/instances.yml
    fi
    bin/elasticsearch-certutil cert \
        --silent \
        --pem \
        --out config/certs/certs.zip \
        --in config/certs/instances.yml \
        --ca-cert config/certs/ca/ca.crt \
        --ca-key config/certs/ca/ca.key
    unzip -q config/certs/certs.zip -d config/certs
fi

chown -R root:root config/certs
find config/certs -type d -exec chmod 755 {} \;
find config/certs -type f -exec chmod 640 {} \;
find config/certs -type f -name '*.crt' -exec chmod 644 {} \;
