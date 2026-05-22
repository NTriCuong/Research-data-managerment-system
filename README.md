# Research Data Management System

Research Data Management System (RDMS) is a monorepo for managing research metadata, review workflows, approved research records, audit logs, and future search indexing with Elasticsearch.

The project currently contains a Next.js frontend, a FastAPI backend, SQLAlchemy models, Alembic migrations, PostgreSQL schema design, and Docker Compose services for PostgreSQL, Elasticsearch, and Kibana.

## Tech Stack

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

### Backend

- Python
- FastAPI
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- JWT authentication utilities
- Elasticsearch client support

### Infrastructure

- npm workspaces
- Docker Compose
- PostgreSQL 16
- Elasticsearch 8
- Kibana 8

## Project Structure

```txt
Research-data-managerment-system/
+-- apps/
|   +-- backend/
|   |   +-- alembic/
|   |   |   +-- env.py
|   |   |   +-- script.py.mako
|   |   |   +-- versions/
|   |   +-- app/
|   |   |   +-- core/
|   |   |   +-- database/
|   |   |   +-- modules/
|   |   |   |   +-- core/
|   |   |   |   +-- logs/
|   |   |   |   +-- stagging/
|   |   |   |   +-- system/
|   |   |   +-- main.py
|   |   +-- .env.example
|   |   +-- alembic.ini
|   +-- frontend/
|   |   +-- app/
|   |   +-- public/
|   |   +-- package.json
|   |   +-- next.config.ts
|   +-- docker-compose.yml
+-- package.json
+-- package-lock.json
+-- README.md
```

## Main Backend Modules

### System Module

The `system` module stores shared system entities in the `public` schema:

- `users`
- `roles`
- `departments`
- `authors`
- `refresh_tokens`

It is used as the base for authentication, authorization, user ownership, reviewers, and audit relationships.

### Staging Module

The `stagging` module stores draft and review data in the `staging` schema:

- `stg_projects`
- `stg_files`
- `stg_keywords`
- `stg_research_authors`
- `stg_reviews`
- `stg_field_comments`

This is the working area for research projects before they are approved into the official dataset.

### Core Module

The `core` module stores approved research data in the `core` schema:

- `core_projects`
- `core_files`
- `core_keywords`
- `core_research_authors`
- `core_edit_logs`
- `core_citations`

This schema represents the official approved data. It is the best source for future Elasticsearch indexing.

### Logs Module

The `logs` module stores operational logs in the `log` schema:

- `audit_logs`
- `login_logs`

These tables are used for tracking user actions, login history, and security/audit events.

## Database Design

The database is organized into four PostgreSQL schemas:

```txt
public   -> users, roles, departments, authors, refresh tokens
staging  -> draft/review research data
core     -> approved research data
log      -> audit and login logs
```

Alembic reads SQLAlchemy metadata from `apps/backend/app/database/config.py`. The migration environment automatically tracks only these schemas:

```txt
public, staging, core, log
```

The initial migration is located at:

```txt
apps/backend/alembic/versions/bc84167c6a36_init_all_schemas.py
```

## Prerequisites

Install these before running the project:

- Node.js 20 or newer
- npm
- Python 3.11 or newer
- PostgreSQL, or Docker Desktop

Docker is recommended because the repository already includes PostgreSQL, Elasticsearch, and Kibana services.

## Install Dependencies

### Frontend and Monorepo Dependencies

From the repository root:

```bash
npm install
```

### Backend Dependencies

From `apps/backend`, create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install the backend libraries:

```bash
pip install fastapi uvicorn sqlalchemy alembic asyncpg psycopg2-binary python-dotenv pydantic-settings python-jose passlib bcrypt elasticsearch
```

Recommended: save them into a `requirements.txt` file later so the backend can be installed with:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a backend environment file:

```bash
cd apps/backend
copy .env.example .env
```

Minimum variables:

```env
FRONTEND_URL=http://localhost:3000
DATABASE_URL=postgresql+asyncpg://postgres:<password>@localhost:5432/<database-name>
SECRET_KEY=change-me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE=30
REFRESH_TOKEN_EXPIRE=7
MAX_LOGIN_ATTEMPTS=5
LOCK_DURATION=15
```

For local Docker Compose, match `DATABASE_URL` with the PostgreSQL service defined in `apps/docker-compose.yml`.

## Run Infrastructure

From the `apps` folder:

```bash
docker compose up -d
```

Services:

```txt
PostgreSQL     http://localhost:5432
Elasticsearch  http://localhost:9200
Kibana         http://localhost:5601
```

## Run Database Migrations

From `apps/backend`:

```bash
venv\Scripts\activate
alembic upgrade head
```

Create a new migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe change"
```

Generate SQL from migrations without applying them:

```bash
alembic upgrade head --sql > design.sql
```

## Run the Backend

From `apps/backend`:

```bash
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

Backend URL:

```txt
http://localhost:8000
```

Current root endpoint:

```txt
GET /
```

Response:

```json
{
  "message": "FastAPI backend is running"
}
```

## Run the Frontend

From the repository root:

```bash
npm run dev:frontend
```

Frontend URL:

```txt
http://localhost:3000
```

## Run Full Development Mode

From the repository root:

```bash
npm run dev
```

This command starts:

- frontend on port `3000`
- backend on port `8000`

If your backend virtual environment is named `venv`, adjust the root `package.json` backend script if needed.

## Elasticsearch Plan

Elasticsearch is included in Docker Compose, but search indexing should be added after the database flow is stable.

Recommended indexing source:

```txt
core.core_projects
```

Suggested searchable fields:

- `identifier`
- `dc_title`
- `dc_creator`
- `dc_description`
- `dc_subject`
- `dc_type`
- `dc_language`
- `status`
- `approved_at`

Recommended sync events:

- index when a project is approved or published
- update when a core project is edited
- hide or delete from index when a project is hidden or retracted

## Current Status

Implemented:

- monorepo setup
- Next.js frontend scaffold
- FastAPI backend scaffold
- SQLAlchemy database config
- PostgreSQL schemas and models
- Alembic migration setup
- initial database migration
- Docker Compose services for PostgreSQL, Elasticsearch, and Kibana
- JWT/password utility files started

Still in progress:

- auth routes and services
- user CRUD
- staging project CRUD
- review and approval workflow
- copying approved staging data into core
- Elasticsearch indexing and search APIs
- production-ready frontend screens

## Useful Commands

```bash
# install frontend dependencies
npm install

# run frontend only
npm run dev:frontend

# run backend only
cd apps/backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# start database/search services
cd apps
docker compose up -d

# run migrations
cd apps/backend
alembic upgrade head

# create migration
alembic revision --autogenerate -m "describe change"
```
