#!/usr/bin/env bash
# Shared only by the two local cluster labs. Source this file; do not execute it.
set -euo pipefail
CLUSTER_LAB=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
REPO_ROOT=$(cd "$CLUSTER_LAB/../../../.." && pwd)
LAB_STATE="$CLUSTER_LAB/.local"
LAB_KUBECONFIG="$LAB_STATE/kubeconfig.yaml"
LAB_CLUSTER=onboarding
LAB_CONTEXT=k3d-onboarding
LAB_REGISTRY=k3d-onboarding-registry.localhost
LAB_K3D_VERSION=v5.9.0
LAB_K3S_IMAGE=rancher/k3s:v1.35.9-k3s1
LAB_REGISTRY_IMAGE=registry:2.8.3

die() { printf 'Error: %s\n' "$*" >&2; exit 1; }
need() { command -v "$1" >/dev/null 2>&1 || die "Install $1; see the lab README."; }

local_docker() {
  need docker
  local endpoint
  if [[ -n "${DOCKER_CONTEXT:-}" ]]; then
    endpoint=$(docker context inspect "$DOCKER_CONTEXT" --format '{{(index .Endpoints "docker").Host}}')
  elif [[ -n "${DOCKER_HOST:-}" ]]; then
    endpoint=$DOCKER_HOST
  else
    endpoint=$(docker context inspect --format '{{(index .Endpoints "docker").Host}}')
  fi
  case "$endpoint" in
    unix://*|npipe://*) ;;
    *) die "This lab requires a local Docker socket; selected endpoint is not local." ;;
  esac
  docker info >/dev/null
}

require_owner() {
  [[ -f "$LAB_STATE/owner" ]] || die "No local lab ownership record. Run scripts/lab.sh create first."
  [[ "$(cat "$LAB_STATE/owner")" == 'onboarding-local-lab-v1' ]] || die "Unexpected ownership record."
}

verify_container() {
  local name=$1 record=$2 actual
  [[ -s "$record" ]] || die "Missing ownership ID for $name; inspect manually instead of deleting a replacement."
  actual=$(docker container inspect --format '{{.Id}}' "$name") || die "Missing $name."
  [[ "$actual" == "$(cat "$record")" ]] || die "Container $name was replaced; refusing to use or delete it."
}

assert_cluster() {
  need kubectl
  local_docker
  require_owner
  verify_container k3d-onboarding-server-0 "$LAB_STATE/server.id"
  [[ -f "$LAB_KUBECONFIG" ]] || die "Missing private lab kubeconfig."
  local context server
  context=$(kubectl --kubeconfig "$LAB_KUBECONFIG" config current-context)
  server=$(kubectl --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" config view --minify -o 'jsonpath={.clusters[0].cluster.server}')
  [[ "$context" == "$LAB_CONTEXT" && "$server" == 'https://127.0.0.1:16443' ]] || die "Kubeconfig does not match the isolated loopback lab."
}

kube() {
  # Keep wrapper callers from replacing the target selected above.
  local arg
  for arg in "$@"; do
    case "$arg" in
      -s*|--kubeconfig*|--context*|--cluster*|--server*|--user*|--token*|--proxy-url*|--insecure-skip-tls-verify*|--client-certificate*|--client-key*|--certificate-authority*|--tls-server-name*)
        die "Target/authentication overrides are not accepted by the lab wrapper." ;;
    esac
  done
  kubectl --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" "$@"
}
