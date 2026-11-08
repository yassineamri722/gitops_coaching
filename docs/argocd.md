# Argo CD deployment with Minikube

This guide configures Argo CD to watch this Git repository and deploy the Helm chart at `helm/taskapp` into the `taskapp` namespace.

The desired flow is:

```text
Git repository -> Argo CD -> Minikube Kubernetes cluster -> taskapp namespace
```

Argo CD is the deployment owner in this flow. Do not continue applying the same application with `kubectl apply -f k8s/` and Helm at the same time.

## GitOps theory

### What GitOps means

GitOps treats Git as the source of truth for the desired state of the cluster. Kubernetes remains the system that runs the workload, but deployment decisions are represented as versioned commits instead of manual commands.

For this project, the desired state includes:

- the Helm chart in `helm/taskapp`;
- replica counts, image repositories, and image tags in `values.yaml`;
- service, Ingress, ConfigMap, Secret, StatefulSet, and Deployment definitions;
- the Argo CD `Application` definition.

The operational rule is:

```text
Change Git -> Argo CD detects the change -> Argo CD reconciles Kubernetes
```

Manual changes made with `kubectl edit`, `kubectl scale`, or an imperative `kubectl apply` are not the desired state. They create drift and can be reverted by Argo CD when `selfHeal` is enabled.

### What Argo CD does

Argo CD is a Kubernetes controller with four main responsibilities:

1. Read the application definition and the requested Git revision.
2. Render the source, here with Helm, into Kubernetes manifests.
3. Compare the rendered desired state with the live cluster state.
4. Synchronize resources when a sync is requested or automated sync is enabled.

Argo CD does not build Docker images and does not replace the CI pipeline. The CI pipeline builds and publishes images; Git records which image tag should be deployed; Argo CD applies that tag.

### Argo CD architecture

The important components in this lab are:

| Component | Responsibility |
| --- | --- |
| `argocd-server` | API server, CLI endpoint, and web UI |
| `argocd-repo-server` | Clones Git repositories and renders Helm/Kustomize sources |
| `argocd-application-controller` | Compares desired and live state and performs reconciliation |
| `argocd-dex-server` | Optional identity integration; useful for SSO in larger environments |
| Redis | Caching used by Argo CD components |

The controller watches `Application` resources. An `Application` is not the workload itself; it is the contract that says which repository, revision, path, cluster, namespace, and synchronization policy should be used.

### Desired state, live state, and drift

An Argo CD Application has two important states:

- **Synced**: the live resources match the manifests rendered from Git.
- **OutOfSync**: at least one live resource differs from the rendered Git state.

Health is separate from synchronization:

- **Healthy**: resources are running and their health checks pass.
- **Degraded**: resources exist but are failing, unavailable, or not ready.
- **Missing**: a resource expected from Git is absent from the cluster.

An application can be `Synced` but `Degraded`: the cluster may exactly match Git while the backend is still in `CrashLoopBackOff`.

### Reconciliation policies

The Application in this guide enables:

```yaml
syncPolicy:
  automated:
    prune: true
    selfHeal: true
```

- `automated` lets Argo CD sync Git changes without a manual button click.
- `prune` deletes resources that were removed from the chart. Use this carefully for data resources.
- `selfHeal` re-applies Git when somebody changes a managed resource manually.
- `CreateNamespace=true` lets Argo CD create `taskapp` if it does not exist.

For a first production rollout, automatic pruning can be disabled until the chart and ownership model are trusted:

```yaml
syncPolicy:
  automated:
    selfHeal: true
    prune: false
```

### Sync, refresh, and rollback

- **Refresh**: Argo CD re-reads Git and recalculates the comparison.
- **Sync**: Argo CD applies the desired manifests to the cluster.
- **Rollback**: Argo CD syncs a previous Git revision or application history entry.

The safest rollback is normally a Git revert because it preserves an auditable deployment history:

```bash
git revert <bad-commit>
git push
argocd app sync taskapp
```

### Why image tags must change in Git

Argo CD reacts to changes in the Git source, not to a Docker registry tag being overwritten and not to a local image rebuild. Reusing `latest` can leave the cluster running an old image because Kubernetes may not pull it again and Argo CD may see no manifest difference.

Use immutable tags, such as a short commit SHA:

```yaml
backend:
  image:
    tag: a1b2c3d
```

The complete release event is then:

```text
CI builds image a1b2c3d
CI pushes image a1b2c3d
CI commits tag a1b2c3d to values.yaml
Argo CD syncs the commit
Kubernetes rolls out the new Deployment pods
```

### Secrets and GitOps

Do not commit real passwords or tokens to Git. The current chart contains a lab password in `values.yaml`; that is acceptable only for disposable local Minikube work.

For a real environment, use one of these approaches:

- External Secrets Operator with a cloud secret manager;
- Sealed Secrets, where only encrypted values are committed;
- SOPS-encrypted values with a controlled decryption key;
- a separately managed secret already present in the target namespace.

Argo CD repository credentials and Kubernetes secrets should be stored in Argo CD or a secret manager, never in an Application manifest committed in plain text.

### Application projects and access control

The examples use the built-in `default` AppProject for a lab. In a shared cluster, create a dedicated `AppProject` that restricts:

- which Git repositories the application may read;
- which clusters and namespaces it may deploy to;
- which Kubernetes resource kinds it may create.

This limits the blast radius of a repository or Application configuration error.

## Prerequisites

Install or verify:

```bash
minikube status
kubectl cluster-info
helm version
```

The chart must render successfully before Argo CD is configured:

```bash
helm lint ./helm/taskapp
helm template taskapp ./helm/taskapp --namespace taskapp > /tmp/taskapp-rendered.yaml
kubectl apply --dry-run=client -f /tmp/taskapp-rendered.yaml
```

The repository must be pushed to Git. Argo CD needs a reachable repository URL, for example:

```text
https://github.com/OWNER/REPOSITORY.git
```

Replace `OWNER/REPOSITORY` in the examples below with the real repository path.

## 1. Install Argo CD

Create the Argo CD namespace and install the official manifest:

```bash
kubectl create namespace argocd
kubectl apply -n argocd \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Wait for the Argo CD components:

```bash
kubectl -n argocd wait --for=condition=available \
  deployment/argocd-server \
  deployment/argocd-repo-server \
  deployment/argocd-application-controller \
  --timeout=180s
```

Check the installation:

```bash
kubectl -n argocd get pods
```

## 2. Open the Argo CD API and UI

In a separate terminal, keep this port-forward running:

```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

The UI is available at:

```text
https://localhost:8080
```

Retrieve the initial administrator password:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath='{.data.password}' | base64 -d
printf '\n'
```

Install the Argo CD CLI if it is not already installed, then log in:

```bash
argocd login localhost:8080 \
  --username admin \
  --password '<INITIAL_PASSWORD>' \
  --insecure
```

Change the initial password after the first login:

```bash
argocd account update-password
```

## 3. Configure access to the Git repository

For a public repository, no additional repository credential is required.

For a private HTTPS repository, register a GitHub token with Argo CD. Do not commit the token to Git:

```bash
argocd repo add https://github.com/OWNER/REPOSITORY.git \
  --username GITHUB_USERNAME \
  --password '<GITHUB_TOKEN>'
```

Verify the repository connection:

```bash
argocd repo list
```

For SSH instead of HTTPS:

```bash
argocd repo add git@github.com:OWNER/REPOSITORY.git \
  --ssh-private-key-path ~/.ssh/id_ed25519
```

## 4. Define the Argo CD Application

Create a local file named `argocd-taskapp.yaml` with the following content. The `repoURL` and `targetRevision` must match the Git repository and branch containing the chart.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: taskapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/OWNER/REPOSITORY.git
    targetRevision: main
    path: helm/taskapp
    helm:
      valueFiles:
        - values.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: taskapp
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

Apply the Application:

```bash
kubectl apply -f argocd-taskapp.yaml
```

This uses the in-cluster API address `https://kubernetes.default.svc`, so no separate cluster registration is needed for the Minikube cluster where Argo CD is installed.

Check the Application:

```bash
kubectl -n argocd get application taskapp
argocd app get taskapp
```

Trigger the first synchronization manually if automated sync has not started yet:

```bash
argocd app sync taskapp
argocd app wait taskapp --health --sync
```

The expected state is:

```text
Sync Status:    Synced
Health Status:  Healthy
```

## 5. Verify the deployed resources

```bash
kubectl -n taskapp get pods,svc,statefulset,deployments,pvc,ingress
```

The expected workloads are:

```text
taskapp-backend-*     Running
taskapp-frontend-*    Running
taskapp-postgres-0    Running
```

Check the backend logs if it is not ready:

```bash
kubectl -n taskapp logs deployment/taskapp-backend --tail=100
kubectl -n taskapp describe pod -l app.kubernetes.io/component=backend
```

Check the database service used by the backend:

```bash
kubectl -n taskapp get svc taskapp-postgres
kubectl -n taskapp get secret taskapp-secret \
  -o jsonpath='{.data.DATABASE_URL}' | base64 -d
printf '\n'
```

The generated database URL should use the Kubernetes service name `taskapp-postgres`.

## 6. Access the application locally

The chart currently exposes frontend and backend Services as `ClusterIP`. For a quick local check, use two port-forwards:

```bash
kubectl -n taskapp port-forward svc/taskapp-frontend 3000:3000
kubectl -n taskapp port-forward svc/taskapp-backend 8000:8000
```

Open:

```text
http://localhost:3000
```

The backend health endpoint is:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

For this access mode, `config.corsOrigins` must include `http://localhost:3000`. One way to provide the value through Argo CD is to add this Helm override to the Application:

```yaml
  source:
    repoURL: https://github.com/OWNER/REPOSITORY.git
    targetRevision: main
    path: helm/taskapp
    helm:
      valuesObject:
        config:
          corsOrigins: http://localhost:3000,http://taskapp.local
```

A more reproducible approach is to place the desired value in a committed values file and reference it from `valueFiles`.

## 7. Ingress notes

The chart defines the host `taskapp.local` and routes `/api`, `/health`, and `/ready` to the backend. The Ingress controller must be available:

```bash
minikube addons enable ingress
kubectl -n taskapp get ingress
```

Find the Minikube IP:

```bash
minikube ip
```

Add the host to `/etc/hosts` with administrator privileges:

```text
<MINIKUBE_IP> taskapp.local
```

Then test the Ingress:

```bash
curl -H 'Host: taskapp.local' http://$(minikube ip)/health
```

The current frontend JavaScript builds its API URL using port `8000`. Therefore, the simplest reliable test for the current code is the two-port-forward method above. Before relying on the Ingress for browser API calls, the frontend should use the same-origin `/api` path or another API URL that matches the Ingress routing.

## CI/CD and Argo CD integration

The current workflow in `.github/workflows/ci-cd.yml` already performs the CI part:

1. Run backend tests.
2. Build backend and frontend images.
3. Scan the images with Trivy.
4. Push images on a push event.

Its final `deploy` job is currently only a placeholder. Argo CD should remain responsible for applying Kubernetes changes. CI should publish an immutable image tag and update the Helm values that Argo CD watches.

### Recommended release contract

Use the short Git commit SHA as the image tag:

```text
backend image:  DOCKERHUB_OWNER/gitops-coaching-backend:<short-sha>
frontend image: DOCKERHUB_OWNER/gitops-coaching-frontend:<short-sha>
```

Then commit the same tag to `helm/taskapp/values.yaml`. That commit is the deployment request. Argo CD notices it, renders the chart, and rolls out the Deployments.

### Example deploy job for this repository

The following job can replace the current deploy placeholder. It assumes the images were pushed to Docker Hub and that the workflow has `contents: write` permission.

```yaml
  deploy:
    name: Update GitOps image tags
    runs-on: ubuntu-latest
    needs: container
    if: github.event_name == 'push' && github.ref == 'refs/heads/master'
    permissions:
      contents: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install yq
        run: |
          sudo wget -qO /usr/local/bin/yq \
            https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
          sudo chmod +x /usr/local/bin/yq

      - name: Update Helm image tags
        env:
          DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          OWNER="$DOCKERHUB_USERNAME"
          if [ -z "$OWNER" ]; then
            OWNER="${GITHUB_REPOSITORY%%/*}"
          fi
          TAG="${IMAGE_TAG:0:7}"
          BACKEND_IMAGE="$OWNER/gitops-coaching-backend"
          FRONTEND_IMAGE="$OWNER/gitops-coaching-frontend"

          BACKEND_IMAGE="$BACKEND_IMAGE" \
          FRONTEND_IMAGE="$FRONTEND_IMAGE" \
          IMAGE_TAG="$TAG" \
          yq -i '
            .backend.image.repository = strenv(BACKEND_IMAGE) |
            .backend.image.tag = strenv(IMAGE_TAG) |
            .frontend.image.repository = strenv(FRONTEND_IMAGE) |
            .frontend.image.tag = strenv(IMAGE_TAG)
          ' helm/taskapp/values.yaml

      - name: Commit GitOps change
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add helm/taskapp/values.yaml
          git commit -m "chore: deploy ${GITHUB_SHA::7} [skip ci]" || exit 0
          git push
```

The `[skip ci]` marker prevents the values-only commit from starting another image build. For a larger organization, keep application source and environment manifests in separate repositories; then CI opens a pull request in the environment repository instead of committing deployment values into the application repository.

### Why Argo CD does not deploy after an image build alone

This does not trigger a deployment by itself:

```bash
docker push OWNER/gitops-coaching-backend:a1b2c3d
```

Argo CD does not continuously inspect registry tags. This does trigger a deployment:

```yaml
backend:
  image:
    repository: OWNER/gitops-coaching-backend
    tag: a1b2c3d
```

Once that change is committed and pushed, Argo CD detects the Git revision and synchronizes the Helm release.

## 8. Image strategy

The current `values.yaml` uses local image names and the `latest` tag:

```yaml
frontend:
  image:
    repository: gitops_coaching-frontend
    tag: latest

backend:
  image:
    repository: gitops_coaching-backend
    tag: latest
```

For Minikube-only development, load locally built images into Minikube:

```bash
docker build -t gitops_coaching-backend:latest ./backend
docker build -t gitops_coaching-frontend:latest ./frontend
minikube image load gitops_coaching-backend:latest
minikube image load gitops_coaching-frontend:latest
```

Argo CD detects Git changes, not a local Docker rebuild with the same tag. For a GitOps workflow, publish immutable image tags to a registry and commit the new tags to `values.yaml`, for example:

```yaml
frontend:
  image:
    repository: ghcr.io/OWNER/gitops-coaching-frontend
    tag: a1b2c3d

backend:
  image:
    repository: ghcr.io/OWNER/gitops-coaching-backend
    tag: a1b2c3d
```

After the commit is pushed, Argo CD detects the values change and creates a new rollout automatically.

## 9. Migrating from kubectl or Helm

Use one deployment owner for the application. Do not run these flows simultaneously:

```bash
kubectl apply -f k8s/
helm upgrade taskapp ./helm/taskapp -n taskapp
argocd app sync taskapp
```

The intended final state is:

```text
Argo CD -> helm/taskapp -> taskapp namespace
```

Before handing ownership to Argo CD, inspect the current resources:

```bash
helm list -n taskapp
kubectl -n taskapp get all,pvc,secret,configmap,ingress
```

Do not delete the PostgreSQL PVC unless the database data can be lost. In a disposable Minikube environment, a clean migration can be performed only after confirming that data loss is acceptable:

```bash
helm uninstall taskapp -n taskapp
kubectl delete -f k8s/ --ignore-not-found
```

Then let Argo CD recreate the application from Git:

```bash
kubectl apply -f argocd-taskapp.yaml
argocd app sync taskapp
```

If existing resources must be preserved, migrate them carefully rather than deleting them. Argo CD can manage resources after synchronization, but resource names, selectors, namespaces, and immutable StatefulSet fields must match the chart.

## 10. Useful Argo CD commands

```bash
argocd app list
argocd app get taskapp
argocd app diff taskapp
argocd app sync taskapp
argocd app wait taskapp --health --sync
argocd app history taskapp
argocd app logs taskapp
```

Pause and resume automated synchronization:

```bash
argocd app set taskapp --sync-policy none
argocd app set taskapp --auto-prune --self-heal
```

Delete the Argo CD Application without deleting its managed Kubernetes resources:

```bash
kubectl -n argocd delete application taskapp --cascade=orphan
```

Delete the Application and allow Argo CD to prune its managed resources:

```bash
kubectl -n argocd delete application taskapp
```

Use the second command carefully, especially because the chart manages PostgreSQL storage.

## Troubleshooting checklist

### Application is `Missing`

Check the repository URL, branch, chart path, and repository credentials:

```bash
argocd app get taskapp
argocd repo list
```

The chart path must be exactly:

```text
helm/taskapp
```

### Application is `OutOfSync`

Inspect the rendered difference:

```bash
argocd app diff taskapp
```

Then synchronize:

```bash
argocd app sync taskapp
```

### Backend is `CrashLoopBackOff`

Check the logs and database service:

```bash
kubectl -n taskapp logs deployment/taskapp-backend --previous
kubectl -n taskapp get svc taskapp-postgres
kubectl -n taskapp get pod taskapp-postgres-0
```

The backend connects to PostgreSQL during startup, so PostgreSQL must be running and the generated `DATABASE_URL` must reference `taskapp-postgres`.

### Pods show `ErrImagePull` or `ImagePullBackOff`

The image is not available to the Minikube node or the registry credentials are missing. Use `minikube image load` for local images, or publish the image to a registry and use a fully qualified repository name in `values.yaml`.

### Changes do not create new pods

Argo CD only reacts to Git changes. Rebuilding an image with the same tag does not create a Git diff. Use a new immutable image tag and commit it to the Helm values.
