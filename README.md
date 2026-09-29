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
.env.example
```

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- A modern web browser

## Configuration

Create a `.env` file from the `.env.example` template:

```bash
cp .env.example .env
```

Edit `.env` with your actual configuration values:

```bash
# Database Configuration
DATABASE_URL=postgresql://taskapp:taskapp@localhost:5432/taskapp

# CORS Configuration (allowed frontend origins)
CORS_ORIGINS=http://localhost:3000

# Frontend API Configuration
API_URL=http://localhost:8000
```

### Security Notes

- **Never commit `.env` files** - They contain sensitive credentials
- `.env` files are already in `.gitignore`
- Always use `.env.example` as a template for developers
- Use strong, unique passwords for database credentials in production
- Change default passwords before deployment

## Configure PostgreSQL

Create a local database and user, for example:

```sql
CREATE USER taskapp WITH PASSWORD 'your_secure_password';
CREATE DATABASE taskapp OWNER taskapp;
```

## Run with Docker Compose

The easiest way to run the entire stack:

```bash
# Create .env from template
cp .env.example .env

# Edit .env with your configuration
# nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The application will be available at `http://localhost:3000`.

## Run the backend manually

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set environment variables before running
export DATABASE_URL='postgresql://taskapp:taskapp@localhost:5432/taskapp'
export CORS_ORIGINS='http://localhost:3000'

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

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://taskapp:taskapp@localhost:5432/taskapp` | PostgreSQL connection string |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated list of allowed CORS origins |
| `API_URL` | `http://localhost:8000` | Backend API URL (used by frontend) |
| `POSTGRES_USER` | `postgres` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `POSTGRES_DB` | `postgres` | PostgreSQL database name |

## Next DevOps steps

1. Add application tests and improve configuration management.
2. Create container images and local orchestration configuration.
3. Add Kubernetes manifests and a Helm chart in a separate GitOps repository.
4. Deploy locally to Minikube, then connect Argo CD and EKS.
5. Provision AWS infrastructure with Terraform.

No container, Kubernetes, cloud, or infrastructure files are included at this stage.
