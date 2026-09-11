#!/usr/bin/env bash
# Fast-start script for the llmware Kubernetes reference deployment.
#
# Builds the existing scripts/docker/Dockerfile image (or reuses one you
# already built/pushed), loads it into the current kubectl context's
# cluster if that context looks like a local kind/minikube cluster, and
# applies the manifests in scripts/kubernetes/base/ via kustomize.
#
# Usage:
#   scripts/kubernetes/fast-start.sh [image-tag]
#
# Requires: kubectl (with kustomize support, kubectl >=1.14), and docker
# (only if you don't already have an image built/pushed).
set -euo pipefail

IMAGE_TAG="${1:-llmware:latest}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

command -v kubectl >/dev/null 2>&1 || {
  echo "kubectl is required but was not found on PATH" >&2
  exit 1
}

CURRENT_CONTEXT="$(kubectl config current-context 2>/dev/null || echo "")"
echo "Using kubectl context: ${CURRENT_CONTEXT:-<none>}"

if command -v docker >/dev/null 2>&1; then
  echo "Building ${IMAGE_TAG} from scripts/docker/Dockerfile ..."
  docker build -t "${IMAGE_TAG}" -f "${REPO_ROOT}/scripts/docker/Dockerfile" "${REPO_ROOT}"

  case "${CURRENT_CONTEXT}" in
    kind-*)
      KIND_CLUSTER="${CURRENT_CONTEXT#kind-}"
      echo "Detected kind cluster '${KIND_CLUSTER}', loading image ..."
      kind load docker-image "${IMAGE_TAG}" --name "${KIND_CLUSTER}"
      ;;
    minikube)
      echo "Detected minikube context, loading image ..."
      minikube image load "${IMAGE_TAG}"
      ;;
    *)
      echo "Not a local kind/minikube context - assuming ${IMAGE_TAG} is already" \
           "reachable by your cluster (e.g. pushed to a registry). If not," \
           "push it and update the image in scripts/kubernetes/base/llmware-deployment.yaml" \
           "before continuing."
      ;;
  esac
else
  echo "docker not found on PATH - assuming ${IMAGE_TAG} is already built and" \
       "reachable by your cluster."
fi

APPLY_DIR="${SCRIPT_DIR}/base"
if [ "${IMAGE_TAG}" != "llmware:latest" ]; then
  echo "Overriding image to ${IMAGE_TAG} ..."
  OVERLAY_DIR="$(mktemp -d)"
  trap 'rm -rf "${OVERLAY_DIR}"' EXIT
  RELATIVE_BASE="$(realpath --relative-to="${OVERLAY_DIR}" "${SCRIPT_DIR}/base")"
  cat > "${OVERLAY_DIR}/kustomization.yaml" <<EOF
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ${RELATIVE_BASE}
images:
  - name: llmware
    newName: ${IMAGE_TAG%%:*}
    newTag: ${IMAGE_TAG##*:}
EOF
  APPLY_DIR="${OVERLAY_DIR}"
fi

echo "Applying manifests ..."
kubectl apply -k "${APPLY_DIR}"

echo "Waiting for mongodb to be ready ..."
kubectl -n llmware rollout status statefulset/mongodb --timeout=180s

echo "Waiting for llmware to be ready ..."
kubectl -n llmware rollout status deployment/llmware --timeout=180s

cat <<'EOF'

llmware is deployed. To run something inside the pod:

  kubectl -n llmware exec -it deploy/llmware -- /bin/bash

Inside the pod, point llmware at the in-cluster MongoDB (already wired via
the llmware-config ConfigMap / COLLECTION_DB_URI) with, e.g.:

  from llmware.configs import LLMWareConfig
  LLMWareConfig.set_active_db("mongo")

EOF
