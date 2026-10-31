# Lab 04: Local reconciliation with Flux

Publish a tiny desired-state snapshot to your local OCI registry, let Flux apply it, observe drift correction, then promote and roll back a second snapshot. No GitHub account, Git server, organization access, or external registry is needed. Allow roughly 60–90 minutes at your own pace.

Complete [lab 03](../03-k3s/README.md) first and keep its `onboarding` cluster running. That lab imports `onboarding-status:0.1.0` into the node. Install the pinned [Flux CLI v2.9.4](https://github.com/fluxcd/flux2/releases/tag/v2.9.4), verify the release checksum, and add it to your PATH. The lab uses `kubectl`, Docker, k3d, and `curl` from lab 03. Flux controller images are public downloads; the work itself stays in your local environment.

## Follow the delivery path

```text
Local YAML files → rendered manifest → local OCI snapshot (v1/v2)
                                           ↓
                               Flux OCIRepository fetches it
                                           ↓
                               Flux Kustomization applies it
                                           ↓
                                  Kubernetes workloads
```

This is OCI delivery with GitOps reconciliation principles. It deliberately leaves out hosted Git, pull requests, CI, and automated publication. In a team workflow, Git history/review commonly records desired-state changes, CI publishes a verified artifact, and Flux consumes it. A local file edit here takes effect only after publication and source selection. Treat the published snapshot as the controller's source of truth; editing a live object does not change it. [Flux OCI documentation](https://fluxcd.io/flux/cheatsheets/oci-artifacts/) explains this delivery model.

The registry has two addresses because the host and cluster have separate network namespaces:

| Caller | Address | Purpose |
| --- | --- | --- |
| Your host CLI | `127.0.0.1:15100` | Publish OCI manifests |
| Flux inside k3d | `k3d-onboarding-registry.localhost:5000` | Fetch the same manifests |

Inside a Pod, `localhost` means that Pod, so using the host address in `OCIRepository` would fail. k3d configures resolution of its attached registry. The host publication is loopback only. This disposable registry uses HTTP with no account; the CLI's `--insecure-registry` and the source's `insecure: true` are deliberate local-lab settings. Shared or production registries need their own TLS, authentication, authorization, and artifact trust policy. [OCIRepository fields](https://fluxcd.io/flux/components/source/ocirepositories/) describe source configuration.

## Install and publish

From this directory:

```bash
cd tracks/devops/labs/04-flux   # when starting at repository root
./scripts/gitops.sh render
./scripts/gitops.sh install
./scripts/gitops.sh publish v1
./scripts/gitops.sh connect
./scripts/gitops.sh status
```

The render command is offline. It composes the previous lab's base into the separate `onboarding-gitops` namespace. The installer targets only the private lab kubeconfig, installs pinned Flux controllers, and refuses to adopt an existing `flux-system` namespace. Only source-controller and kustomize-controller are needed. These controllers have broad rights inside this disposable cluster; this exercise is not a multi-tenant RBAC design. [Flux installation](https://fluxcd.io/flux/installation/) and [install command](https://fluxcd.io/flux/cmd/flux_install/) provide background.

`flux check` may report that a newer CLI release is available. This lab uses a tested version pair; verify that the Kubernetes prerequisites, controllers, and CRD checks also pass. An update notice alone does not mean installation failed. Review upstream compatibility guidance before changing the pinned versions.

`publish` packages only the rendered toy manifests and a Kustomize entrypoint, never your entire working tree or kubeconfig. Each tag gets a digest receipt under ignored `.local/`. The helper refuses to overwrite a tag so the rollback example retains the original bytes. [Artifact publication](https://fluxcd.io/flux/cmd/flux_push_artifact/) documents the underlying command. There is no automatic Git commit or remote upload.

Expect `Ready=True` for both Flux objects and one ready application replica. Open a local connection:

```bash
./scripts/gitops.sh port-forward
# In another terminal:
curl --fail http://127.0.0.1:18084/readyz
```

Stop port forwarding with Ctrl+C before later cleanup.

## Observe drift correction

Manually change the live replica count through the cluster wrapper:

```bash
../03-k3s/scripts/lab.sh kubectl -n onboarding-gitops scale deployment/status --replicas=3
../03-k3s/scripts/lab.sh kubectl -n onboarding-gitops get deployment status
./scripts/gitops.sh reconcile
../03-k3s/scripts/lab.sh kubectl -n onboarding-gitops get deployment status
```

The desired replica count returns to one. It may already be corrected by the periodic reconciliation before you inspect it. Flux corrects managed fields using the selected snapshot. Describe its reconciliation object to inspect conditions and inventory:

```bash
../03-k3s/scripts/lab.sh kubectl -n flux-system describe kustomization status
```

The Kustomize file in `app/` composes YAML locally; the Flux `Kustomization` custom resource schedules apply, health checks, and garbage collection in the cluster. They are different resources. [Flux Kustomization documentation](https://fluxcd.io/flux/components/kustomize/kustomizations/) explains reconciliation and pruning.

## Promote and roll back

Edit `app/kustomization.yaml`, changing the `replicas` count from `1` to `2`. Inspect the render, publish a new immutable teaching snapshot, and select it:

```bash
./scripts/gitops.sh render
./scripts/gitops.sh publish v2
./scripts/gitops.sh select v2
./scripts/gitops.sh status
```

Expect two ready replicas. Publishing alone does not promote a snapshot: `controllers/source.yaml` initially selects `v1`, and the helper's `select` changes that control-plane reference. Roll back by selecting the retained snapshot:

```bash
./scripts/gitops.sh select v1
./scripts/gitops.sh status
```

Expect one replica again. Restore the file's count to `1` so your working directory matches the rolled-back intent. Also restore or record `controllers/source.yaml` when choosing a lasting version: running `connect` reapplies that file and selects its declared tag. In an approved team workflow the version reference would be changed through reviewed source control. Image rollback is not a database restore; this service has no persistent data or migrations.

For a stronger identity check, compare the source's observed artifact digest with the receipt in `.local/v1.json`. OCI tags can be mutable outside this helper; production promotion often pins an artifact digest and verifies its signature rather than relying on a tag's name.

## Troubleshoot and clean up

For `Ready=False`, inspect conditions before restarting anything:

```bash
../03-k3s/scripts/lab.sh kubectl -n flux-system describe ocirepository status
../03-k3s/scripts/lab.sh kubectl -n flux-system logs deployment/source-controller --tail=30
../03-k3s/scripts/lab.sh kubectl -n flux-system logs deployment/kustomize-controller --tail=30
```

Check the registry name/port, that the tag was published, namespace, image import, and node resources. An `ImagePullBackOff` for the toy app usually means lab 03 did not import the image into this cluster. Keep logs free of credentials before sharing them.

`prune: true` means resources removed from a selected snapshot are deleted from Flux's inventory on reconciliation. Here the inventory includes the application's Namespace, so pruning it removes its contents. Never add valuable data to this disposable namespace.

```bash
./scripts/gitops.sh uninstall
../03-k3s/scripts/lab.sh delete
```

Uninstall deletes the Flux Kustomization first and waits for its inventory cleanup while the controllers are still alive, then removes the source and Flux. The second command removes the recorded cluster and registry. Generated receipts/rendered files may remain in ignored `.local/`; discard them when no longer useful. Do not remove controller finalizers to bypass an unexplained cleanup failure.
