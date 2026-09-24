# Task Management App

A small three-tier task-management application prepared for later DevOps work.

## Architecture

- **Frontend:** static HTML/CSS/JavaScript
- **Backend:** FastAPI REST API
- **Database:** PostgreSQL

The browser calls the backend; only the backend connects to PostgreSQL.

## Repository structure

```text
frontend/
  index.html
backend/
  app/main.py
  requirements.txt
README.md
```

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- A modern web browser

## Configure PostgreSQL

Create a local database and user, for example:

```sql
CREATE USER taskapp WITH PASSWORD 'taskapp';
CREATE DATABASE taskapp OWNER taskapp;
```

The backend uses these environment variables:

```bash
export DATABASE_URL='postgresql://taskapp:taskapp@localhost:5432/taskapp'
export CORS_ORIGINS='http://localhost:3000'
```

## Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`. Interactive API documentation is available at `http://localhost:8000/docs`.

## Run the frontend

In a second terminal, from the repository root:

```bash
python -m http.server 3000 --directory frontend
```

Open `http://localhost:3000` in a browser.

## API endpoints

- `GET /health` - liveness check
- `GET /ready` - database readiness check
- `GET /api/tasks` - list tasks
- `POST /api/tasks` - create a task
- `PATCH /api/tasks/{id}` - update completion state
- `DELETE /api/tasks/{id}` - delete a task

## Next DevOps steps

1. Add application tests and improve configuration management.
2. Create container images and local orchestration configuration.
3. Add Kubernetes manifests and a Helm chart in a separate GitOps repository.
4. Deploy locally to Minikube, then connect Argo CD and EKS.
5. Provision AWS infrastructure with Terraform.

No container, Kubernetes, cloud, or infrastructure files are included at this stage.
