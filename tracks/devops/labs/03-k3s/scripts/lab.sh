#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

usage() {
  cat <<'EOF'
Usage: scripts/lab.sh create | deploy | status | port-forward | delete
       scripts/lab.sh kubectl <arguments>
Run only on your own disposable learning environment. All names are fixed.
EOF
}

create() {
  need k3d; need kubectl; need jq
  local_docker
  [[ "$(k3d version | sed -n '1p')" == "k3d version $LAB_K3D_VERSION" ]] || die "Use k3d $LAB_K3D_VERSION."
  [[ ! -e "$LAB_STATE/owner" ]] || die "Existing lab record; inspect status or delete the recorded lab first."
  if k3d cluster list -o json | jq -e '.[] | select(.name == "onboarding")' >/dev/null; then
    die "A cluster named onboarding already exists; this script will not adopt it."
  fi
  if docker container inspect "$LAB_REGISTRY" >/dev/null 2>&1; then
    die "The named registry already exists; this script will not adopt it."
  fi
  if docker network inspect k3d-onboarding >/dev/null 2>&1; then
    die "The named lab network already exists; inspect its owner before creating a cluster."
  fi
  umask 077
  mkdir -p "$LAB_STATE"
  printf '%s\n' 'onboarding-local-lab-v1' > "$LAB_STATE/owner"
  k3d registry create onboarding-registry.localhost \
    --port 127.0.0.1:15100 --image "$LAB_REGISTRY_IMAGE"
  docker container inspect --format '{{.Id}}' "$LAB_REGISTRY" > "$LAB_STATE/registry.id"
  if ! k3d cluster create "$LAB_CLUSTER" \
    --servers 1 --agents 0 --servers-memory 4g \
    --image "$LAB_K3S_IMAGE" --api-port 127.0.0.1:16443 \
    --registry-use "$LAB_REGISTRY:5000" \
    --k3s-arg '--disable=traefik@server:0' \
    --k3s-arg '--disable=servicelb@server:0' \
    --kubeconfig-update-default=false --kubeconfig-switch-context=false \
    --wait --timeout 180s; then
    docker container inspect --format '{{.Id}}' k3d-onboarding-server-0 > "$LAB_STATE/server.id" 2>/dev/null || true
    die "Cluster creation failed. Inspect k3d cluster list and this README's cleanup guidance."
  fi
  docker container inspect --format '{{.Id}}' k3d-onboarding-server-0 > "$LAB_STATE/server.id"
  k3d kubeconfig get "$LAB_CLUSTER" > "$LAB_KUBECONFIG"
  chmod 600 "$LAB_KUBECONFIG"
  assert_cluster
  kube wait --for=condition=Ready node/k3d-onboarding-server-0 --timeout=180s
  printf 'Created local lab. API: 127.0.0.1:16443; registry: 127.0.0.1:15100.\n'
}

deploy() {
  assert_cluster
  need k3d
  # This is an original toy image from this repository, built in the Docker lab.
  docker image inspect onboarding-status:0.1.0 >/dev/null || die "Build onboarding-status:0.1.0 from examples/status-service first."
  k3d image import onboarding-status:0.1.0 --cluster "$LAB_CLUSTER"
  kube apply -k "$CLUSTER_LAB/manifests"
  kube -n onboarding-demo rollout status deployment/status --timeout=180s
}

delete_lab() {
  need k3d
  local_docker
  require_owner
  local has_cluster=false has_registry=false
  # Validate all recorded resources before removing either one.
  if docker container inspect k3d-onboarding-server-0 >/dev/null 2>&1; then
    verify_container k3d-onboarding-server-0 "$LAB_STATE/server.id"
    has_cluster=true
  fi
  if docker container inspect "$LAB_REGISTRY" >/dev/null 2>&1; then
    verify_container "$LAB_REGISTRY" "$LAB_STATE/registry.id"
    has_registry=true
  fi
  # Remove the attached registry first so cluster deletion can remove its network.
  if "$has_registry"; then
    k3d registry delete onboarding-registry.localhost
  fi
  if "$has_cluster"; then
    KUBECONFIG="$LAB_KUBECONFIG" k3d cluster delete "$LAB_CLUSTER"
  fi
  rm -f "$LAB_STATE/kubeconfig.yaml" "$LAB_STATE/server.id" "$LAB_STATE/registry.id" "$LAB_STATE/owner"
  printf 'Removed only the recorded onboarding cluster and local registry.\n'
}

case "${1:-help}" in
  create) create ;;
  deploy) deploy ;;
  status) assert_cluster; kube get nodes; kube -n onboarding-demo get deployments,pods,services ;;
  port-forward) assert_cluster; kube -n onboarding-demo port-forward --address=127.0.0.1 service/status 18083:8080 ;;
  kubectl) shift; assert_cluster; kube "$@" ;;
  delete) delete_lab ;;
  help|-h|--help) usage ;;
  *) usage >&2; exit 2 ;;
esac
