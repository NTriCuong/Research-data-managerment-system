# RDMS deployment

Production uses two internal servers:

- App server: Nginx, frontend, backend and PostgreSQL from `compose.yaml`.
- Elasticsearch server: the existing official Elastic Docker Compose cluster.

PostgreSQL is the source of truth. Elasticsearch contains a rebuildable search index. Email, push notification and index synchronization run in the FastAPI process through `BackgroundTasks`.

## 1. Prepare the existing Elasticsearch server

Do not run `compose.elasticsearch.yaml` on the production Elasticsearch server. It is retained for local development only.

The official Elastic Compose certificate contains `es01`, `localhost` and `127.0.0.1` by default. The app containers therefore use `https://es01:9200` and map `es01` to the Elasticsearch server IP through Compose `extra_hosts`. If the Elastic administrator issues a certificate for a different internal DNS name, use that name consistently instead.

On the Elasticsearch server, from the directory containing Elastic's official `docker-compose.yml`, export the public CA:

```bash
docker compose cp es01:/usr/share/elasticsearch/config/certs/ca/ca.crt /tmp/rdms-elasticsearch-ca.crt
```

Copy the RDMS repository or at least its provisioning script and mapping to this server. Put the exported CA at `deploy/elasticsearch/certs/ca.crt`, then configure the one-time administrator environment:

```bash
cp .env.elasticsearch-admin.example .env.elasticsearch-admin
```

Set a random URL-safe `RDMS_ELASTIC_PASSWORD` without quotes or backslashes, and the existing Elastic administrator password. Provision only the RDMS resources:

```bash
bash deploy/scripts/provision-shared-elasticsearch.sh
```

This creates:

- role `rdms_backend_role`, restricted to `rdms_research_objects*`;
- user `rdms_backend`;
- index `rdms_research_objects_v1` with the English search analyzer;
- write alias `rdms_research_objects`.

Analyzer settings are immutable after index creation. If `rdms_research_objects_v1` already exists without `rdms_english`, the provisioning script stops; create a new versioned index, reindex, and switch the alias instead of modifying the existing index in place.

The script does not change `kibana_system`, cluster certificates or other teams' indices. Keep `.env.elasticsearch-admin` only on the Elasticsearch server and never copy the `elastic` password to the app server.

Allow only the app server IP to access TCP `9200`. Do not publish Elasticsearch or Kibana to the Internet.

## 2. Prepare the app server

Transfer `/tmp/rdms-elasticsearch-ca.crt` from the Elasticsearch server to:

```text
deploy/elasticsearch/certs/ca.crt
```

The CA certificate is public. Do not transfer `ca.key`, node private keys or the whole Elastic certificate volume.

Create the app environment:

```bash
cp .env.example .env
```

Set the Elasticsearch connection values:

```dotenv
ELASTIC_SERVER_IP=10.0.0.20
ELASTIC_CERT_HOSTNAME=es01
ELASTIC_HOST=https://es01:9200
ELASTIC_USERNAME=rdms_backend
RDMS_ELASTIC_PASSWORD=<same value used during provisioning>
ELASTIC_CA_CERT_HOST_PATH=./deploy/elasticsearch/certs/ca.crt
ELASTIC_INDEX=rdms_research_objects
```

`ELASTIC_HOST` must use a DNS name or IP present in the node certificate SAN. TLS verification remains enabled in production.

Deploy the app stack:

```bash
bash deploy/scripts/deploy.sh
bash deploy/scripts/health-check.sh
```

The deployment runs Alembic migrations and then starts the web application. Redis and separate task workers are not required.

## 3. Approve and indexing flow

An approve request commits the core record, audit and workflow logs first. Only after that commit succeeds does it register FastAPI background tasks for Elasticsearch indexing and user notification. The indexing task receives only `research_id`, opens a new database session, loads the committed aggregate and upserts it through alias `rdms_research_objects` using the database ID as Elasticsearch `_id`.

These tasks are intentionally best-effort and process-local: an application restart can interrupt them and there is no durable retry queue. PostgreSQL remains authoritative, so Elasticsearch can be rebuilt from committed core records when reconciliation is required.

Core search at `GET /api/v1/search/core` uses Elasticsearch BM25 and exact filters through the read alias. Public research listing also uses Elasticsearch whenever a text search or structured filter is supplied. PostgreSQL remains authoritative: the backend rebuilds role-based access filters from PostgreSQL and verifies/hydrates each returned record there. If Elasticsearch is unavailable, both flows fall back to the existing PostgreSQL search implementation.

To enable FCM, mount the Firebase service-account JSON read-only at the path configured by `FIREBASE_CREDENTIALS_PATH`. When that file is absent, push notifications are safely skipped.

## 4. Local development

For local development only, the repository can start its own single-node Elasticsearch stack:

```bash
cp .env.example .env
cp .env.elasticsearch.example .env.elasticsearch

docker compose \
  --env-file .env \
  --env-file .env.elasticsearch \
  -f compose.yaml \
  -f compose.elasticsearch.yaml \
  -f compose.dev.yaml \
  up -d --build
```

The two environment files must use the same `RDMS_ELASTIC_PASSWORD`.

## 5. Operations

```bash
bash deploy/scripts/migrate.sh
bash deploy/scripts/seed.sh
bash deploy/scripts/backup-postgres.sh
bash deploy/scripts/health-check.sh
```

Restore requires explicit target confirmation:

```bash
CONFIRM_RESTORE=yes bash deploy/scripts/restore-postgres.sh deploy/backups/rdms-TIMESTAMP.dump
```

Do not commit environment files, administrator credentials, private keys, backups or Elasticsearch snapshots.
