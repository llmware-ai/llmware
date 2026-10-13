# Kubernetes reference deployment

A reference Kubernetes configuration for running llmware in a cluster,
complementing the existing Docker/devcontainer scripts in
[`scripts/docker`](../docker). It deploys:

- `llmware` — a Deployment built from [`scripts/docker/Dockerfile`](../docker/Dockerfile),
  kept running so you can `kubectl exec` into it to run llmware scripts/pipelines.
- `mongodb` — a single-replica StatefulSet, used as the default collection
  database (mirrors the `mongodb` service in
  [`scripts/docker/docker-compose.yaml`](../docker/docker-compose.yaml)).

Manifests are plain [Kustomize](https://kustomize.io/) (no Helm, no
templating) so they stay easy to read and fork for other vector/collection
databases the same way the Docker Compose files do.

## Layout

```
scripts/kubernetes/
  fast-start.sh       # builds/loads the image and applies everything below
  base/
    namespace.yaml
    llmware-configmap.yaml
    llmware-deployment.yaml
    mongodb-statefulset.yaml
    kustomization.yaml
```

## Fast start

Local cluster (kind or minikube), from the repo root:

```bash
scripts/kubernetes/fast-start.sh
```

This builds the image from `scripts/docker/Dockerfile`, loads it into a
detected local kind/minikube cluster, applies the manifests, and waits for
both workloads to become ready.

Already-built/pushed image on a remote cluster:

```bash
scripts/kubernetes/fast-start.sh myregistry/llmware:v1
```

Or apply directly without the script (if you already have an image
reachable by your cluster and have set it in
`base/llmware-deployment.yaml`):

```bash
kubectl apply -k scripts/kubernetes/base
```

## Using it

```bash
kubectl -n llmware exec -it deploy/llmware -- /bin/bash
```

Inside the pod, the collection database URI is already wired via the
`llmware-config` ConfigMap (`COLLECTION_DB_URI`, read by
`llmware.configs.MongoConfig`). Select mongo as the active backend the same
way you would locally:

```python
from llmware.configs import LLMWareConfig
LLMWareConfig.set_active_db("mongo")
```

## Scaling / extending

- Storage: `llmware-data` and `mongodb-data` PVCs default to 10Gi/5Gi —
  adjust in `base/llmware-deployment.yaml` / `base/mongodb-statefulset.yaml`
  for your workload.
- Other databases: add a Kustomize overlay (`scripts/kubernetes/overlays/<db>/`)
  the same way `scripts/docker/docker-compose-<db>.yaml` covers Postgres,
  Milvus, Qdrant, Neo4j, Redis — not included here to keep this reference
  minimal; contributions welcome.
- Multiple llmware replicas: the app itself is stateless aside from the
  collection/vector DB, so `spec.replicas` on the `llmware` Deployment can
  be raised once you're driving it via a script/entrypoint rather than
  `kubectl exec`.
