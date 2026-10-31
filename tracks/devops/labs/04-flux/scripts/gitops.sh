#!/usr/bin/env bash
set -euo pipefail
FLUX_LAB=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source "$FLUX_LAB/../03-k3s/scripts/common.sh"
FLUX_VERSION=2.9.4

usage() {
  cat <<'EOF'
Usage: scripts/gitops.sh render | install | publish TAG | connect | select TAG
       scripts/gitops.sh reconcile | status | port-forward | uninstall
Uses only the lab-03 onboarding cluster and its private kubeconfig.
EOF
}

require_flux() {
  need flux
  [[ "$(flux --version)" == "flux version $FLUX_VERSION" ]] || die "Use Flux CLI $FLUX_VERSION."
}

flux_lab() {
  flux --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" "$@"
}

owned_flux() {
  assert_cluster
  require_flux
  [[ -s "$FLUX_LAB/.local/controller-cluster.id" ]] || die "No recorded lab Flux installation; run install."
  cmp -s "$FLUX_LAB/.local/controller-cluster.id" "$LAB_STATE/server.id" || die "Flux record belongs to an older cluster; run install on this new cluster."
}

tag_argument() {
  [[ $# -eq 1 && "$1" =~ ^v[0-9]+$ ]] || die "Supply one new snapshot tag such as v1 or v2."
}

render() {
  need kubectl
  # Kustomize rendering is local and does not consult the selected cluster.
  kubectl kustomize "$FLUX_LAB/app"
}

install() {
  assert_cluster
  require_flux
  if kube get namespace flux-system >/dev/null 2>&1; then
    die "flux-system already exists. Use status; reset this disposable cluster rather than adopting another installation."
  fi
  umask 077
  mkdir -p "$FLUX_LAB/.local"
  cp "$LAB_STATE/server.id" "$FLUX_LAB/.local/controller-cluster.id"
  flux_lab check --pre
  flux_lab install --version "v$FLUX_VERSION" \
    --components=source-controller,kustomize-controller \
    --watch-all-namespaces=false --timeout=5m
  flux_lab check
}

publish() {
  tag_argument "$@"
  local tag=$1 response artifact_dir
  owned_flux
  need curl
  verify_container "$LAB_REGISTRY" "$LAB_STATE/registry.id"
  # Refuse to overwrite a teaching snapshot: rollback needs the old bytes.
  response=$(curl --silent --show-error --max-time 10 --output /dev/null --write-out '%{http_code}' \
    -H 'Accept: application/vnd.oci.image.manifest.v1+json' \
    "http://127.0.0.1:15100/v2/onboarding/manifests/manifests/$tag")
  [[ "$response" == 404 ]] || die "Expected an unused tag (HTTP 404); registry returned $response. Choose a new tag or inspect registry health."
  umask 077
  # A fresh staging directory cannot accidentally include files from an earlier run.
  artifact_dir=$(mktemp -d "$FLUX_LAB/.local/artifact.XXXXXX")
  trap 'rm -rf -- "$artifact_dir"' RETURN
  render > "$artifact_dir/manifest.yaml"
  cat > "$artifact_dir/kustomization.yaml" <<'EOF'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - manifest.yaml
EOF
  # Publish only the rendered toy manifests, never the whole repository or kubeconfig.
  flux push artifact "oci://127.0.0.1:15100/onboarding/manifests:$tag" \
    --path "$artifact_dir" --source 'file:///onboarding' \
    --revision "$tag" --insecure-registry --output json > "$FLUX_LAB/.local/$tag.json"
  printf 'Published %s to the local registry. Digest receipt: .local/%s.json\n' "$tag" "$tag"
}

reconcile() {
  owned_flux
  flux_lab reconcile source oci status --timeout=2m
  flux_lab reconcile kustomization status --with-source --timeout=3m
}

uninstall() {
  owned_flux
  # Keep the controllers running while the Kustomization finalizer prunes its inventory.
  kube -n flux-system delete kustomization status --ignore-not-found --wait=true --timeout=180s
  kube -n flux-system delete ocirepository status --ignore-not-found
  flux_lab uninstall --silent
  rm -f "$FLUX_LAB/.local/controller-cluster.id"
}

case "${1:-help}" in
  render) render ;;
  install) install ;;
  publish) shift; publish "$@" ;;
  connect) owned_flux; kube apply -f "$FLUX_LAB/controllers"; reconcile ;;
  select)
    shift; tag_argument "$@"; owned_flux
    kube -n flux-system patch ocirepository status --type merge -p "{\"spec\":{\"ref\":{\"tag\":\"$1\"}}}"
    reconcile ;;
  reconcile) reconcile ;;
  status)
    owned_flux
    flux_lab get sources oci
    flux_lab get kustomizations
    kube -n onboarding-gitops get deployments,pods,services ;;
  port-forward) owned_flux; kube -n onboarding-gitops port-forward --address=127.0.0.1 service/status 18084:8080 ;;
  uninstall) uninstall ;;
  help|-h|--help) usage ;;
  *) usage >&2; exit 2 ;;
esac
