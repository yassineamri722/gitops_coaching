# GitHub Actions CI/CD Guide

This repository uses GitHub Actions to demonstrate a complete CI/CD flow without GitOps or Kubernetes deployment. The goal is to show the mechanics of a modern pipeline first, then hand deployment over to a later Argo CD and Minikube stage.

## Pipeline overview

The workflow is split into three logical parts:

1. Quality gate: checkout, install dependencies, run tests, and scan the code with SonarCloud.
2. Container gate: build the backend and frontend images, scan them with Trivy, and publish them to Docker Hub.
3. Deploy gate: echo a placeholder message that marks the handoff point to the future GitOps flow.

## Theoretical notions

### Checkout

Checkout means fetching the repository content onto the GitHub Actions runner. Every later step depends on the source tree being present.

### Build

Build turns source code into a runnable artifact. In this repository, the build stage is the Docker image build for both the backend API and the static frontend.

### Test

Test verifies that the application behaves as expected before release. The backend test suite exercises the API in isolation with a fake in-memory database so the workflow does not depend on an external PostgreSQL instance.

### Code scan

Code scanning checks the source itself for quality and security issues. Here it is represented by SonarCloud analyzing the backend code and tests.

### Docker image scan

Image scanning checks the container artifact after it is built. This is the last point where image issues can be detected before publication.

### Push to Docker Hub

Publishing the image stores the built artifact in Docker Hub so later environments can pull the exact same image digest or tag.

### Deploy

The final stage is intentionally simple. It exists to show where deployment would happen, but it only echoes a message and does not apply Kubernetes manifests or GitOps synchronization yet.

## Why there is no GitOps or Kubernetes stage yet

GitOps works best when the deployment target is managed from a separate declarative repository and a controller such as Argo CD. This repository stops before that boundary on purpose:

1. The CI/CD path is easier to understand in isolation.
2. The current focus is image production and release hygiene.
3. The real deployment mechanics will be introduced later with Minikube and Argo CD.

## Required GitHub secrets

Set these repository secrets before enabling the push stage:

1. `DOCKERHUB_USERNAME`
2. `DOCKERHUB_TOKEN`
3. `SONAR_TOKEN`

## Local equivalents

You can mirror the quality gate locally from the `backend/` directory with:

```bash
python -m pip install -r requirements.txt pytest httpx
pytest
```

The Docker image build can be reproduced from the repository root with the existing Dockerfiles.