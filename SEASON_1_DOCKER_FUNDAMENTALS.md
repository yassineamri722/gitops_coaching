# 🐳 Docker Coaching - Season 1: Docker Fundamentals & Dockerfiles

## Table of Contents
1. [Introduction](#introduction)
2. [Core Docker Concepts](#core-docker-concepts)
3. [Why Docker?](#why-docker)
4. [Installation & Setup](#installation--setup)
5. [Understanding Dockerfiles](#understanding-dockerfiles)
6. [Dockerfile Instructions](#dockerfile-instructions)
7. [Project Structure](#project-structure)
8. [Creating Backend Dockerfile](#creating-backend-dockerfile)
9. [Creating Frontend Dockerfile](#creating-frontend-dockerfile)
10. [Building Images](#building-images)
11. [Understanding Layers](#understanding-layers)
12. [Best Practices](#best-practices)
13. [Practical Exercises](#practical-exercises)
14. [Common Mistakes](#common-mistakes)
15. [Summary & Key Takeaways](#summary--key-takeaways)

---

## Introduction

Welcome to Season 1 of Docker Coaching! In this season, we will focus on understanding Docker fundamentals and creating Dockerfiles for both backend and frontend applications.

By the end of this season, you will:
- ✅ Understand what Docker is and why it's important
- ✅ Know how to write a Dockerfile
- ✅ Build Docker images
- ✅ Understand image layers and caching
- ✅ Follow Docker best practices

**Project**: We will containerize a Task Management Application with:
- Frontend: Static HTML/CSS/JavaScript
- Backend: FastAPI REST API
- Database: PostgreSQL (in later sessions)

---

## Core Docker Concepts

### What is Docker?

**Docker** is a containerization platform that allows you to package your application and all its dependencies into a standardized unit called a **container**.

```
Traditional Approach:
App Code → Dependencies → System Libraries → OS
(Might work on Dev, breaks on Production)

Docker Approach:
App Code → Dependencies → System Libraries → Docker Container
(Works everywhere the Docker Engine is installed)
```

### Key Definitions

#### 1. Container
A **container** is a lightweight, standalone, executable package that contains everything needed to run an application:
- Application code
- Runtime environment
- System dependencies
- Libraries
- Environment variables

**Characteristics:**
- Isolated (own filesystem, network, processes)
- Lightweight (megabytes, not gigabytes)
- Portable (runs the same everywhere)
- Fast to start and stop

#### 2. Image
An **image** is a blueprint or template for creating containers. It's like a class in object-oriented programming.

```
Image = Class
Container = Instance of the class
```

**Characteristics:**
- Immutable (read-only)
- Layered (composed of multiple layers)
- Portable (can be moved between systems)
- Versioned (can have tags like v1.0, latest)

#### 3. Dockerfile
A **Dockerfile** is a text file containing a series of instructions to build a Docker image.

**Analogy**: A recipe for baking a cake
- Ingredients = Base image + dependencies
- Instructions = RUN, COPY, etc.
- Final product = Docker image

#### 4. Docker Registry
A **registry** is a centralized repository for storing and sharing Docker images.

**Popular registries:**
- Docker Hub (default, public)
- Amazon ECR (AWS)
- Google Container Registry (GCP)
- GitHub Container Registry
- Private registries

#### 5. Docker Engine
The **Docker Engine** is the core software that builds, runs, and manages containers.

---

## Why Docker?

### Problems Docker Solves

#### Problem 1: "It Works on My Machine"

```
Developer's Machine:
- Python 3.9, PostgreSQL 12, Node.js 14
- Works perfectly ✓

Production Server:
- Python 3.7, PostgreSQL 10, Node.js 12
- Application crashes ✗
```

**Docker Solution:**
Package the exact environment in a container. Same environment everywhere.

#### Problem 2: Dependency Hell

```
App Dependencies:
- Library A requires Python 3.8
- Library B requires Python 3.10
- Can't install both in system Python ✗

Docker Solution:
Each container has its own Python version.
No conflicts!
```

#### Problem 3: Environment Setup Complexity

```
Traditional Setup:
1. Install Python
2. Install PostgreSQL
3. Install Node.js
4. Install Redis
5. Set environment variables
6. Configure networking
= Hours of setup

Docker Setup:
docker run [app]
= Seconds!
```

### Benefits of Docker

| Benefit | Description |
|---------|-------------|
| **Consistency** | Same environment across dev, test, and production |
| **Isolation** | Applications don't interfere with each other |
| **Portability** | Works on Windows, Mac, Linux, Cloud |
| **Scalability** | Easy to run multiple containers |
| **Efficiency** | Lightweight, minimal resource overhead |
| **Reproducibility** | Same image always produces same behavior |
| **Faster Development** | No more setup nightmares |
| **Microservices** | Each service in its own container |

### Docker Use Cases

```
1. Local Development
   Developer → Docker Container = Production-like environment locally

2. CI/CD Pipeline
   Build → Test → Docker Image → Deploy

3. Microservices
   Frontend Container | Backend Container | Database Container
   (Each independent, can scale separately)

4. Deployment
   Push image to registry → Pull to production → Run container

5. Multiple Versions
   App v1.0 | App v2.0 | App v3.0
   (Run different versions in different containers)
```

---

## Installation & Setup

### Check if Docker is Installed

```bash
docker --version
```

**Expected output:**
```
Docker version 24.0.0, build 12345
```

### Check Docker Compose

```bash
docker compose version
```

**Expected output:**
```
Docker Compose version v2.20.0
```

### Installation Steps

#### Windows & Mac
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Run the installer
3. Follow the setup wizard
4. Restart your computer

#### Linux (Ubuntu/Debian)
```bash
# Update package manager
sudo apt-get update

# Install Docker
sudo apt-get install docker.io docker-compose

# Add user to docker group (optional, allows running docker without sudo)
sudo usermod -aG docker $USER

# Verify
docker --version
docker compose version
```

### Test Docker Installation

```bash
docker run hello-world
```

**Expected output:**
```
Hello from Docker!
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon
 2. The Docker daemon pulled the "hello-world" image
 3. The Docker daemon created a new container from that image
 4. The Docker daemon streamed that output to the Docker client
 5. The Docker client sent it to your terminal

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

To learn more and get more help with docker, visit https://docs.docker.com/
```

**What just happened?**
1. Docker checked if `hello-world` image exists locally
2. It didn't, so Docker pulled it from Docker Hub
3. Docker created a container from the image
4. The container ran and printed the message
5. The container stopped

---

## Understanding Dockerfiles

### What is a Dockerfile?

A **Dockerfile** is a text file with instructions to build a Docker image.

```
Dockerfile → Docker Build → Docker Image → docker run → Container
   (Text)      (Process)      (Binary)      (Execution)  (Running)
```

### Dockerfile Structure

A Dockerfile typically has this structure:

```dockerfile
# Step 1: Choose base image
FROM python:3.11-slim

# Step 2: Set working directory
WORKDIR /app

# Step 3: Copy files
COPY requirements.txt .

# Step 4: Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy application code
COPY app/ ./app/

# Step 6: Expose port (documentation)
EXPOSE 8000

# Step 7: Define default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Why Layered Approach?

Docker images are built in **layers**. Each instruction creates a new layer.

```
Dockerfile:
  FROM python:3.11-slim           → Layer 1 (base image)
  WORKDIR /app                    → Layer 2 (filesystem)
  COPY requirements.txt .         → Layer 3 (add file)
  RUN pip install ...             → Layer 4 (install deps)
  COPY app/ ./app/                → Layer 5 (add app code)
  EXPOSE 8000                     → Layer 6 (metadata)
  CMD ["uvicorn", ...]            → Layer 7 (metadata)

Final Image = Stack of all layers
```

### Layer Caching

Docker caches layers for efficiency. If a layer hasn't changed, Docker reuses it.

```
Build 1:
  FROM python:3.11-slim           → Build layer 1 (15 seconds)
  WORKDIR /app                    → Build layer 2 (1 second)
  COPY requirements.txt .         → Build layer 3 (1 second)
  RUN pip install ...             → Build layer 4 (30 seconds)
  COPY app/ ./app/                → Build layer 5 (1 second)
  Total: 48 seconds

Build 2 (only app changed):
  FROM python:3.11-slim           → Use cache (0 seconds)
  WORKDIR /app                    → Use cache (0 seconds)
  COPY requirements.txt .         → Use cache (0 seconds)
  RUN pip install ...             → Use cache (0 seconds)
  COPY app/ ./app/                → Build layer 5 (1 second)
  Total: 1 second ⚡

This is why order matters!
```

---

## Dockerfile Instructions

### Complete Reference

#### FROM

**Purpose**: Specify the base image

```dockerfile
FROM python:3.11-slim
```

**Notes:**
- Must be the first instruction (except ARG)
- Choose base image wisely (affects final size)
- Always use specific versions, not `latest`

**Base Image Examples:**
```dockerfile
FROM python:3.11-slim          # ~150MB, good for Python apps
FROM python:3.11-alpine        # ~50MB, very lightweight
FROM node:18-alpine            # ~150MB, for JavaScript
FROM nginx:alpine              # ~40MB, for web servers
FROM ubuntu:22.04              # ~77MB, general purpose
FROM scratch                   # 0MB, empty (advanced)
```

#### WORKDIR

**Purpose**: Set the working directory inside the container

```dockerfile
WORKDIR /app
```

**Effect:**
- Creates directory if it doesn't exist
- All subsequent commands run from this directory

```dockerfile
WORKDIR /app
COPY . .           # Copies to /app
RUN ls             # Lists /app contents
```

#### COPY

**Purpose**: Copy files from host to container

```dockerfile
COPY requirements.txt .        # Copy single file
COPY . .                       # Copy entire directory
COPY app/ ./app/               # Copy directory to specific location
```

**Format:**
```dockerfile
COPY <src-on-host> <dest-in-container>
```

**vs ADD:**
- COPY: Simple file copying (preferred)
- ADD: Can download from URLs, auto-extract tar files (advanced)

#### RUN

**Purpose**: Execute commands during build

```dockerfile
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y curl
```

**Shell vs Exec form:**
```dockerfile
# Shell form (has shell)
RUN pip install -r requirements.txt

# Exec form (no shell)
RUN ["pip", "install", "-r", "requirements.txt"]
```

**Best practices:**
```dockerfile
# ❌ Bad - Multiple RUN commands, multiple layers
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y wget

# ✅ Good - Combine into one layer
RUN apt-get update && apt-get install -y curl wget
```

#### ENV

**Purpose**: Set environment variables

```dockerfile
ENV DATABASE_URL=postgresql://localhost/myapp
ENV DEBUG=False
ENV PYTHONUNBUFFERED=1
```

**Usage in container:**
```bash
echo $DATABASE_URL        # Prints: postgresql://localhost/myapp
```

#### EXPOSE

**Purpose**: Document which ports the container listens on

```dockerfile
EXPOSE 8000
EXPOSE 5000 3000
```

**Important:** EXPOSE doesn't actually publish ports!

```dockerfile
EXPOSE 8000          # Documents that app runs on 8000
```

When running:
```bash
docker run -p 8000:8000 app:1.0    # Publishes the port
docker run app:1.0                 # EXPOSE documented, but port not published
```

#### CMD

**Purpose**: Default command to run when container starts

```dockerfile
CMD ["python", "app.py"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

**Shell vs Exec form:**
```dockerfile
# Shell form
CMD python app.py

# Exec form (preferred)
CMD ["python", "app.py"]
```

**Can be overridden:**
```bash
docker run myapp                          # Uses CMD from Dockerfile
docker run myapp python other.py          # Overrides CMD
```

#### ENTRYPOINT

**Purpose**: Configure container as an executable

```dockerfile
ENTRYPOINT ["python", "-m", "uvicorn"]
CMD ["app.main:app", "--host", "0.0.0.0"]
```

**Difference from CMD:**
```dockerfile
ENTRYPOINT ["python"]
CMD ["app.py"]
# Result: python app.py

# Override:
docker run myapp other.py          # python other.py ✓
docker run myapp                   # python ✓
```

vs

```dockerfile
CMD ["python", "app.py"]

# Override:
docker run myapp other.py          # other.py ✗ (doesn't use python)
docker run myapp                   # python app.py ✓
```

#### HEALTHCHECK

**Purpose**: Monitor container health

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

**Parameters:**
- `--interval`: How often to check (default: 30s)
- `--timeout`: How long to wait for response (default: 30s)
- `--start-period`: Grace period before starting checks (default: 0s)
- `--retries`: Failed checks before marking unhealthy (default: 3)

**Example with Python:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
```

#### ARG

**Purpose**: Build-time variables

```dockerfile
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim
```

**Usage:**
```bash
docker build --build-arg PYTHON_VERSION=3.10 .
```

#### USER

**Purpose**: Run container as specific user (security)

```dockerfile
RUN useradd -m appuser
USER appuser
```

---

## Project Structure

Before writing Dockerfiles, let's understand our project structure.

### Directory Layout

```
gitops_coaching/
├── backend/
│   ├── app/
│   │   └── main.py           # FastAPI application
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Backend container recipe
│   └── .dockerignore          # Files to ignore in build
├── frontend/
│   ├── index.html             # Frontend UI
│   ├── Dockerfile             # Frontend container recipe
│   └── .dockerignore          # Files to ignore in build
├── docker-compose.yml         # Multi-container orchestration
├── .env.example               # Environment variables template
├── README.md                  # Project documentation
└── Makefile                   # Automation commands
```

### Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI app
│   └── models.py             # Data models
├── requirements.txt          # pip dependencies
├── Dockerfile
├── .dockerignore
└── tests/                    # Unit tests
```

### Frontend Structure

```
frontend/
├── index.html                # Main HTML page
├── style.css                 # Styles
├── script.js                 # JavaScript
├── Dockerfile
└── .dockerignore
```

---

## Creating Backend Dockerfile

### Step-by-Step Breakdown

#### Step 1: Choose Base Image

```dockerfile
FROM python:3.11-slim
```

**Why `python:3.11-slim`?**
- Size: ~150MB (smaller than full image)
- Includes Python 3.11 and pip
- Includes basic system packages
- Ideal for backend applications

**Alternative base images:**
```dockerfile
FROM python:3.11           # Full image (~900MB)
FROM python:3.11-alpine    # Alpine Linux (~50MB, fewer packages)
FROM python:3.10-slim      # If need Python 3.10
```

#### Step 2: Set Working Directory

```dockerfile
WORKDIR /app
```

**What it does:**
- Creates `/app` directory in container
- Changes to this directory for all subsequent commands

```dockerfile
WORKDIR /app
# All subsequent commands work from /app
COPY . .       # Copies to /app
RUN ls         # Lists /app
```

#### Step 3: Copy Requirements File

```dockerfile
COPY requirements.txt .
```

**Why separate?**
- Layer caching optimization
- If only code changes, dependencies aren't reinstalled
- Faster rebuilds

```
Without separation:
  COPY . .              # Layer 1 (code + requirements)
  RUN pip install ...   # Layer 2 (install)
  # Change code → Both layers rebuild ✗

With separation:
  COPY requirements.txt .    # Layer 1 (requirements)
  RUN pip install ...        # Layer 2 (install, cached)
  COPY app/ ./app/           # Layer 3 (code)
  # Change code → Only layer 3 rebuilds ✓
```

#### Step 4: Install Dependencies

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```

**Why `--no-cache-dir`?**
- Pip caches downloaded packages
- Cache not needed in container
- Reduces image size by ~20-30MB

**Before:**
```dockerfile
RUN pip install -r requirements.txt
# Image size: ~450MB
```

**After:**
```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
# Image size: ~420MB (30MB smaller!)
```

#### Step 5: Copy Application Code

```dockerfile
COPY app/ ./app/
```

**After dependencies are installed**, copy the actual application code.

**Why after?**
- Application code changes frequently
- Dependencies rarely change
- Layer caching keeps installation cached
- Faster rebuilds during development

#### Step 6: Expose Port

```dockerfile
EXPOSE 8000
```

**Documentation:** Tells users/tools that app listens on 8000.

**Note:** Doesn't actually publish the port. Publishing happens at runtime with `-p`.

#### Step 7: Add Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
```

**What it does:**
- Checks if app is responsive
- Runs `/health` endpoint every 30 seconds
- If fails 3 times → container marked as unhealthy
- Essential for orchestration tools

#### Step 8: Set Default Command

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**What it does:**
- Starts the FastAPI application
- Listens on all interfaces (`0.0.0.0`)
- Runs on port 8000
- This command runs when container starts

### Complete Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Save File

Create `backend/Dockerfile`:

```bash
touch backend/Dockerfile
```

Copy the complete Dockerfile above into this file.

---

## Creating Frontend Dockerfile

The frontend is simpler since it's static HTML.

### Frontend Dockerfile Breakdown

#### Step 1: Base Image

```dockerfile
FROM python:3.11-slim
```

For static files, Python's built-in HTTP server is perfect.

#### Step 2: Working Directory

```dockerfile
WORKDIR /app
```

#### Step 3: Copy Frontend Files

```dockerfile
COPY . .
```

Copy all frontend files (HTML, CSS, JS).

#### Step 4: Expose Port

```dockerfile
EXPOSE 3000
```

Frontend runs on port 3000 in development.

#### Step 5: Run HTTP Server

```dockerfile
CMD ["python", "-m", "http.server", "3000", "--directory", "."]
```

**What it does:**
- Python's built-in HTTP server
- Serves files from current directory
- Listens on port 3000
- Perfect for development

### Complete Frontend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .

EXPOSE 3000

CMD ["python", "-m", "http.server", "3000", "--directory", "."]
```

### Save File

Create `frontend/Dockerfile`:

```bash
touch frontend/Dockerfile
```

Copy the complete Dockerfile above into this file.

---

## Creating .dockerignore

Similar to `.gitignore`, `.dockerignore` excludes files from Docker builds.

### Why .dockerignore?

Smaller build context = faster builds and smaller images.

```
Without .dockerignore:
  Docker context: All files including node_modules, venv, .git, etc.
  Build context size: ~500MB
  Build time: 30 seconds

With .dockerignore:
  Docker context: Only app files
  Build context size: ~1MB
  Build time: 1 second
```

### Backend .dockerignore

Create `backend/.dockerignore`:

```dockerignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
.venv
venv/
env/
ENV/
*.egg-info/
dist/
build/

# Version Control
.git
.gitignore
.gitlab-ci.yml
.github/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.*.local

# Documentation
*.md
README.md

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Docker
Dockerfile
docker-compose.yml
.dockerignore
```

### Frontend .dockerignore

Create `frontend/.dockerignore`:

```dockerignore
# Version Control
.git
.gitignore
.gitlab-ci.yml
.github/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local

# Documentation
*.md
README.md

# Package managers
node_modules/
npm-debug.log
yarn-error.log
package-lock.json

# OS
.DS_Store
Thumbs.db

# Docker
Dockerfile
docker-compose.yml
.dockerignore
```

---

## Building Images

### What Happens During Build

```
Dockerfile + Build Context → Docker Engine → Image
   (Recipe)      (Files)        (Process)     (Output)
```

### Build Process

1. **Prepare build context** (all files to be copied)
2. **Execute Dockerfile instructions** (step by step)
3. **Create layers** (each RUN, COPY creates a layer)
4. **Cache layers** (for faster future builds)
5. **Create final image** (stack of all layers)

### Build Backend Image

```bash
cd backend
docker build -t task-backend:1.0 .
```

**Breakdown:**
- `docker build`: Build command
- `-t task-backend:1.0`: Tag image (name:version)
- `.`: Build context (current directory)

**Expected output:**

```
Sending build context to Docker daemon  1.234MB
Step 1/8 : FROM python:3.11-slim
 ---> abc123def456
Step 2/8 : WORKDIR /app
 ---> Running in xyz789abc123
 ---> def456abc789
Removing intermediate container xyz789abc123
Step 3/8 : COPY requirements.txt .
 ---> Running in xyz789abc123
 ---> ghi789def456
Removing intermediate container xyz789abc123
Step 4/8 : RUN pip install --no-cache-dir -r requirements.txt
 ---> Running in xyz789abc123
Collecting fastapi==0.115.6
Downloading fastapi-0.115.6-py3-none-any.whl (92kB)
...
Successfully installed fastapi-0.115.6 uvicorn-0.33.0
 ---> jkl123ghi789
Removing intermediate container xyz789abc123
Step 5/8 : COPY app/ ./app/
 ---> Running in xyz789abc123
 ---> mno456jkl123
Removing intermediate container xyz789abc123
Step 6/8 : EXPOSE 8000
 ---> Running in xyz789abc123
 ---> pqr789mno456
Removing intermediate container xyz789abc123
Step 7/8 : HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
 ---> Running in xyz789abc123
 ---> stu123pqr789
Removing intermediate container xyz789abc123
Step 8/8 : CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
 ---> Running in xyz789abc123
 ---> vwx456stu123
Removing intermediate container xyz789abc123
Successfully built vwx456stu123
Successfully tagged task-backend:1.0
```

### Build Frontend Image

```bash
cd frontend
docker build -t task-frontend:1.0 .
```

**Expected output:**

```
Sending build context to Docker daemon  5.678MB
Step 1/4 : FROM python:3.11-slim
 ---> abc123def456
Step 2/4 : WORKDIR /app
 ---> Using cache
 ---> def456abc789
Step 3/4 : COPY . .
 ---> Running in xyz789abc123
 ---> ghi789def456
Step 4/4 : CMD ["python", "-m", "http.server", "3000", "--directory", "."]
 ---> Running in xyz789abc123
 ---> jkl123ghi789
Successfully built jkl123ghi789
Successfully tagged task-frontend:1.0
```

### View Built Images

```bash
docker images
```

**Output:**

```
REPOSITORY          TAG       IMAGE ID      CREATED              SIZE
task-backend        1.0       vwx456stu123  About a minute ago   245MB
task-frontend       1.0       jkl123ghi789  About a minute ago   152MB
python              3.11-slim abc123def456  3 months ago         151MB
```

**Columns:**
- REPOSITORY: Image name
- TAG: Image version/tag
- IMAGE ID: Unique identifier (hash)
- CREATED: When image was built
- SIZE: Compressed image size

### Build with Options

#### Build with no cache

```bash
docker build --no-cache -t task-backend:1.0 .
```

Forces rebuild of all layers (useful when you want fresh installs).

#### Build with different Dockerfile

```bash
docker build -f Dockerfile.prod -t task-backend:1.0-prod .
```

#### Build multiple tags

```bash
docker build -t task-backend:1.0 -t task-backend:latest .
```

---

## Understanding Layers

### What are Layers?

Each instruction in a Dockerfile creates a layer (a filesystem change).

```dockerfile
FROM python:3.11-slim          # Layer 1: Base image
WORKDIR /app                   # Layer 2: Create /app directory
COPY requirements.txt .        # Layer 3: Add requirements.txt
RUN pip install ...            # Layer 4: Install packages
COPY app/ ./app/               # Layer 5: Add app code
EXPOSE 8000                    # Layer 6: Metadata
CMD ["uvicorn", ...]           # Layer 7: Metadata
```

### Viewing Layers

```bash
docker history task-backend:1.0
```

**Output:**

```
IMAGE          CREATED          CREATED BY                                  SIZE      COMMENT
vwx456stu123   2 minutes ago    /bin/sh -c #(nop)  CMD ["uvicorn" "app...  0B
stu123pqr789   2 minutes ago    /bin/sh -c #(nop)  HEALTHCHECK --inter...  0B
pqr789mno456   2 minutes ago    /bin/sh -c #(nop)  EXPOSE 8000             0B
mno456jkl123   2 minutes ago    /bin/sh -c #(nop) COPY dir:abc123 in /a...  15KB
jkl123ghi789   2 minutes ago    /bin/sh -c pip install --no-cache-dir ...  94MB
ghi789def456   2 minutes ago    /bin/sh -c #(nop) COPY file:xyz789 in /...  156B
def456abc789   2 minutes ago    /bin/sh -c #(nop) WORKDIR /app              0B
abc123def456   3 months ago     /bin/sh -c #(nop)  CMD ["python"]           0B
```

### Layer Caching

Docker caches layers for faster rebuilds.

```
First Build:
  Layer 1 (FROM) → Pulled from registry (15 seconds)
  Layer 2 (WORKDIR) → Created (1 second)
  Layer 3 (COPY requirements) → Copied (1 second)
  Layer 4 (RUN pip) → Installed (30 seconds)
  Layer 5 (COPY app) → Copied (1 second)
  Total: 48 seconds

Second Build (only app changed):
  Layer 1 (FROM) → Cached (0 seconds)
  Layer 2 (WORKDIR) → Cached (0 seconds)
  Layer 3 (COPY requirements) → Cached (0 seconds)
  Layer 4 (RUN pip) → Cached (0 seconds)
  Layer 5 (COPY app) → Different → Built (1 second)
  Total: 1 second ⚡
```

### Optimizing Layer Order

**Bad Order (inefficient):**
```dockerfile
FROM python:3.11-slim
COPY app/ ./app/              # App code (changes frequently)
COPY requirements.txt .       # Dependencies (rarely change)
RUN pip install -r requirements.txt
```

**Problem:** Change in app → Entire pip install recached (30 seconds)

**Good Order (efficient):**
```dockerfile
FROM python:3.11-slim
COPY requirements.txt .       # Dependencies first
RUN pip install -r requirements.txt
COPY app/ ./app/              # App code last
```

**Benefit:** Change in app → Only COPY recached (1 second)

### Layer Size

```bash
docker history --no-trunc task-backend:1.0
```

Shows layer sizes:

```
Layer 1 (FROM): 151MB
Layer 4 (RUN pip): 94MB
Other layers: ~5MB
Total: ~250MB
```

---

## Best Practices

### 1. Use Specific Base Image Versions

❌ **Bad:**
```dockerfile
FROM python:latest
FROM node:latest
```

✅ **Good:**
```dockerfile
FROM python:3.11-slim
FROM node:18-alpine
```

**Why:** `latest` tag changes, breaking builds unexpectedly.

### 2. Use .dockerignore

❌ **Bad:**
```bash
# No .dockerignore
# Everything copied (including node_modules, .git, etc.)
```

✅ **Good:**
```dockerignore
node_modules/
.git
.env
__pycache__/
```

**Why:** Reduces build context, speeds up builds.

### 3. Minimize Layers

❌ **Bad:**
```dockerfile
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y wget
RUN apt-get clean
```

✅ **Good:**
```dockerfile
RUN apt-get update && apt-get install -y curl wget && apt-get clean
```

**Why:** Fewer layers = smaller image.

### 4. Order Instructions for Caching

❌ **Bad:**
```dockerfile
COPY . .
RUN pip install -r requirements.txt
```

✅ **Good:**
```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

**Why:** Dependencies cached, app code rebuilt quickly.

### 5. Remove Build Artifacts

❌ **Bad:**
```dockerfile
RUN apt-get install -y build-essential
# Leaves build tools in image
```

✅ **Good:**
```dockerfile
RUN apt-get update && apt-get install -y build-essential && apt-get clean && rm -rf /var/lib/apt/lists/*
```

**Why:** Removes package manager cache, reduces size.

### 6. Use .dockerignore for Secrets

❌ **Bad:**
```dockerfile
COPY . .
# .env file with secrets copied into image!
```

✅ **Good:**
```dockerignore
.env
.env.local
secrets/
```

**Why:** Secrets shouldn't be baked into images.

### 7. Use Environment Variables

❌ **Bad:**
```dockerfile
RUN DATABASE_URL="postgresql://localhost/db" uvicorn app.main:app
```

✅ **Good:**
```dockerfile
ENV DATABASE_URL=postgresql://localhost/db
CMD ["uvicorn", "app.main:app"]
```

**Why:** Can override at runtime.

### 8. Include Health Checks

❌ **Bad:**
```dockerfile
# No health check
CMD ["python", "app.py"]
```

✅ **Good:**
```dockerfile
HEALTHCHECK --interval=30s CMD curl -f http://localhost:8000/health || exit 1
CMD ["python", "app.py"]
```

**Why:** Orchestrators can monitor container health.

### 9. Document Exposed Ports

✅ **Good:**
```dockerfile
EXPOSE 8000
EXPOSE 5000
```

**Why:** Documents which ports container uses.

### 10. Use Non-Root User (Security)

❌ **Bad:**
```dockerfile
CMD ["python", "app.py"]
# Runs as root
```

✅ **Good:**
```dockerfile
RUN useradd -m appuser
USER appuser
CMD ["python", "app.py"]
```

**Why:** Limits damage if container is compromised.

---

## Practical Exercises

### Exercise 1: Build and Verify Images

**Objective:** Build both images and verify they exist.

**Steps:**

```bash
# Navigate to backend
cd backend

# Build backend image
docker build -t task-backend:1.0 .

# Verify backend image
docker images | grep task-backend

# Navigate to frontend
cd ../frontend

# Build frontend image
docker build -t task-frontend:1.0 .

# Verify frontend image
docker images | grep task-frontend

# List all images
docker images
```

**Expected Output:**
```
REPOSITORY          TAG       IMAGE ID      CREATED        SIZE
task-backend        1.0       abc123def456  1 minute ago    245MB
task-frontend       1.0       def456ghi789  1 minute ago    152MB
```

### Exercise 2: View Image Layers

**Objective:** Understand image composition.

**Steps:**

```bash
# View backend layers
docker history task-backend:1.0

# View backend layers with no truncation
docker history --no-trunc task-backend:1.0

# View detailed history
docker history --human task-backend:1.0

# View frontend layers
docker history task-frontend:1.0
```

**What to Look For:**
- Number of layers
- Size of each layer
- Which layers take most space

### Exercise 3: Build with No Cache

**Objective:** Understand layer caching.

**Steps:**

```bash
# First build (with cache)
cd backend
docker build -t task-backend:1.0 .
# Note the time taken

# Second build (should be fast due to cache)
docker build -t task-backend:1.0 .
# Note the time taken (much faster!)

# Build with no cache (force rebuild)
docker build --no-cache -t task-backend:1.0 .
# Note the time taken (slower, like first build)
```

**Observation:**
- First build: ~30-50 seconds
- Second build: ~1-2 seconds (cache!)
- No cache build: ~30-50 seconds

### Exercise 4: Inspect Image Configuration

**Objective:** Understand image metadata.

**Steps:**

```bash
# Inspect backend image
docker inspect task-backend:1.0

# Pretty print JSON
docker inspect task-backend:1.0 | jq '.[0]'

# View specific properties
docker inspect task-backend:1.0 | jq '.[0].Config.Env'
docker inspect task-backend:1.0 | jq '.[0].Config.ExposedPorts'
docker inspect task-backend:1.0 | jq '.[0].Config.Cmd'
```

**Information Visible:**
- Environment variables
- Exposed ports
- Default command
- Working directory
- etc.

### Exercise 5: Build Multiple Tags

**Objective:** Understand image tagging.

**Steps:**

```bash
# Build with version tag
docker build -t task-backend:1.0 backend/

# Add additional tags
docker tag task-backend:1.0 task-backend:latest
docker tag task-backend:1.0 task-backend:stable
docker tag task-backend:1.0 task-backend:v1.0.0

# View all tags
docker images | grep task-backend
```

**Expected Output:**
```
REPOSITORY          TAG       IMAGE ID
task-backend        1.0       abc123def456
task-backend        latest    abc123def456
task-backend        stable    abc123def456
task-backend        v1.0.0    abc123def456
```

**Note:** All point to same IMAGE ID (same image, different names)

---

## Common Mistakes

### Mistake 1: Running as Root

❌ **Problem:**
```dockerfile
FROM python:3.11-slim
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
# Runs as root!
```

✅ **Solution:**
```dockerfile
FROM python:3.11-slim
RUN useradd -m appuser
RUN pip install -r requirements.txt
USER appuser
CMD ["python", "app.py"]
```

### Mistake 2: Using Latest Tag

❌ **Problem:**
```dockerfile
FROM python:latest
# What version is this? Changes over time!
```

✅ **Solution:**
```dockerfile
FROM python:3.11-slim
# Explicit version
```

### Mistake 3: Not Using .dockerignore

❌ **Problem:**
```bash
# No .dockerignore
# Build context includes: node_modules (100MB), .git (50MB), etc.
```

✅ **Solution:**
```dockerignore
node_modules/
.git
.env
```

### Mistake 4: Large Layers

❌ **Problem:**
```dockerfile
RUN apt-get update
RUN apt-get install -y package1
RUN apt-get install -y package2
RUN apt-get install -y package3
# 4 layers, cache issues
```

✅ **Solution:**
```dockerfile
RUN apt-get update && \
    apt-get install -y package1 package2 package3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
# 1 layer, smaller image
```

### Mistake 5: Copying Everything Early

❌ **Problem:**
```dockerfile
COPY . .
RUN pip install -r requirements.txt
# Change code → pip reinstalls (cache broken)
```

✅ **Solution:**
```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# Change code → pip not rerun (cache kept)
```

### Mistake 6: Hardcoding Configuration

❌ **Problem:**
```dockerfile
ENV DATABASE_URL=postgresql://localhost/mydb
ENV DEBUG=True
# Can't change at runtime!
```

✅ **Solution:**
```dockerfile
ENV DATABASE_URL=""
ENV DEBUG=False
# Can override at runtime: -e DATABASE_URL=...
```

### Mistake 7: Not Cleaning Up

❌ **Problem:**
```dockerfile
RUN apt-get install build-essential
# Leaves build tools in final image
```

✅ **Solution:**
```dockerfile
RUN apt-get install build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### Mistake 8: No Health Check

❌ **Problem:**
```dockerfile
CMD ["python", "app.py"]
# Container could be zombie process (running but not responsive)
```

✅ **Solution:**
```dockerfile
HEALTHCHECK --interval=30s CMD curl -f http://localhost/health || exit 1
CMD ["python", "app.py"]
```

---

## Summary & Key Takeaways

### What You've Learned

1. **Docker Concepts**
   - Containers: Isolated, portable packages
   - Images: Blueprints for containers
   - Dockerfiles: Recipes for building images
   - Registries: Storage for sharing images

2. **Dockerfile Instructions**
   - FROM: Base image
   - WORKDIR: Working directory
   - COPY: Copy files
   - RUN: Execute commands
   - EXPOSE: Document ports
   - CMD: Default command
   - HEALTHCHECK: Monitor health

3. **Best Practices**
   - Use specific versions
   - Optimize layer order
   - Use .dockerignore
   - Minimize layers
   - Include health checks
   - Run as non-root user

4. **Layer Caching**
   - Each instruction = one layer
   - Docker caches layers
   - Order matters for performance
   - Separate dependencies from code

5. **Building Images**
   - `docker build -t name:tag .`
   - View layers with `docker history`
   - Inspect with `docker inspect`
   - Multiple tags for same image

### Key Commands

```bash
# Build
docker build -t image:tag .

# View images
docker images

# View layers
docker history image:tag

# Inspect
docker inspect image:tag

# Remove
docker rmi image:tag
```

### Golden Rules

1. ✅ Always use specific base image versions
2. ✅ Put dependencies BEFORE code
3. ✅ Use .dockerignore
4. ✅ Include HEALTHCHECK
5. ✅ Keep images small
6. ✅ Document EXPOSE ports
7. ✅ Run as non-root user
8. ✅ Never hardcode secrets

---

## Next Steps

You've completed Season 1! Here's what comes next:

### Season 2: Building and Running Containers
- Running containers with docker run
- Port mapping and networking
- Environment variables
- Volume mounting
- Debugging containers with logs and exec
- Container lifecycle management

### Season 3: Docker Hub & Image Registry
- Creating Docker Hub account
- Pushing images to registry
- Pulling images
- Image tagging strategy
- Private registries

### Season 4: Docker Compose
- Multi-container orchestration
- docker-compose.yml syntax
- Service networking
- Environment configuration
- Volumes and persistence

### Season 5: Image Optimization
- Alpine Linux base images
- Multi-stage builds
- Distroless images
- Size optimization techniques
- Production-ready images

---

## Resources

### Official Documentation
- [Docker Docs](https://docs.docker.com/)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### Base Images
- [python](https://hub.docker.com/_/python)
- [node](https://hub.docker.com/_/node)
- [nginx](https://hub.docker.com/_/nginx)
- [alpine](https://hub.docker.com/_/alpine)

### Tools
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Docker CLI](https://docs.docker.com/engine/reference/commandline/cli/)
- [Docker Hub](https://hub.docker.com/)

---

# 🎓 Season 1 Complete!

You now understand Docker fundamentals and can write Dockerfiles for your applications.

In the next season, we'll run these containers and connect them together.

**Happy Dockering! 🐳**
