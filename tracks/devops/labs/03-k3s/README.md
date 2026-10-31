# Lab 03: Kubernetes on your own machine

Deploy the original status service onto a disposable, one-node K3s cluster. Read the rendered objects, diagnose a failed rollout, and remove the lab without touching another cluster. Plan roughly 60–90 minutes at your own pace.

This exercise uses k3d to run K3s inside Docker. It does not describe a company cluster. There is no cloud account, hosted VM, public ingress, or paid infrastructure. Internet access is needed to download tools and public images; downloads use local disk and bandwidth.

## Prerequisites

Use your own Linux machine/VM or Docker Desktop environment with Bash, Docker CLI/engine, `curl`, `jq`, and these pinned tools:

| Component | Lab version | Official reference |
| --- | --- | --- |
| k3d | `v5.9.0` | [Release and binaries](https://github.com/k3d-io/k3d/releases/tag/v5.9.0) |
| K3s node image | `rancher/k3s:v1.35.9-k3s1` | [K3s 1.35 releases](https://docs.k3s.io/release-notes/v1.35.X) |
| kubectl | `v1.35.9` | [Install kubectl and verify its checksum](https://kubernetes.io/docs/tasks/tools/) |
| Local OCI registry image | `registry:2.8.3` | [Distribution registry](https://distribution.github.io/distribution/) |

Choose the binary matching your CPU and OS and check the publisher's checksums before installing. The scripts do not download or run remote installation scripts. A Linux VM with about 4 CPU cores, 8 GiB RAM, and 20 GiB free disk is a reasonable starting allocation for both cluster labs; the single K3s node has a 4 GiB container memory limit. Performance varies by host. This is not a high-availability exercise.

Build the toy image from the repository root before proceeding:

```bash
docker build -t onboarding-status:0.1.0 examples/status-service
cd tracks/devops/labs/03-k3s
```

The scripts require a local Unix/named-pipe Docker socket and reject remote TCP/SSH Docker endpoints. In Docker Desktop, host port publications appear on the machine running Desktop. If you use a VM, run commands and `curl` inside that VM or deliberately forward only its loopback ports to your own machine.

## Create and inspect

```bash
./scripts/lab.sh create
./scripts/lab.sh deploy
./scripts/lab.sh status
./scripts/lab.sh kubectl -n onboarding-demo get events --sort-by=.lastTimestamp
```

The fixed lab name is `onboarding`. Kubernetes listens at `127.0.0.1:16443`; a local registry listens at `127.0.0.1:15100` for the next lab. Existing resources with those names cause the script to stop. If either port is occupied, inspect the owner and stop here rather than replacing it.

The create command explicitly disables default kubeconfig updates and context switching. Credentials go into ignored `.local/kubeconfig.yaml` with owner-only permissions. The wrapper checks the context, loopback API URL, and recorded Docker container ID before cluster operations. Use it for this lab instead of changing your regular Kubernetes context. Kubeconfig contains credentials: keep `.local/` private.

Review `manifests/` and its local render:

```bash
kubectl kustomize manifests
```

The Deployment requests a small CPU/memory budget and runs one replica with no service-account token. Its process runs as UID 10001 with a read-only root filesystem, dropped Linux capabilities, and the runtime's seccomp profile. The Namespace requests Kubernetes' restricted Pod Security policy. [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) explain these controls. k3d itself uses privileged node containers; run it only where you are permitted to run Docker-based Kubernetes.

The Service uses a label selector to find ready Pods. A startup probe allows startup time; readiness controls whether a Pod receives Service traffic; liveness can restart a stuck container. [Probe documentation](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/) describes their different purposes. These are HTTP checks of a toy process, not proof that a whole business workflow succeeds.

## Make a request

Keep this command running in one terminal:

```bash
./scripts/lab.sh port-forward
```

In a second terminal:

```bash
curl --fail http://127.0.0.1:18083/healthz
curl --fail http://127.0.0.1:18083/readyz
curl --fail http://127.0.0.1:18083/version
```

Each request should succeed with HTTP 200. Stop port forwarding with Ctrl+C when done; the application remains deployed. No NodePort, LoadBalancer Service, or public tunnel is needed.

## Diagnose and recover

Introduce an unavailable image tag, then inspect the resulting state:

```bash
./scripts/lab.sh kubectl -n onboarding-demo set image deployment/status status=onboarding-status:does-not-exist
./scripts/lab.sh kubectl -n onboarding-demo get pods
./scripts/lab.sh kubectl -n onboarding-demo describe deployment status
./scripts/lab.sh kubectl -n onboarding-demo get events --sort-by=.lastTimestamp
```

Expect image-pull failures on the new Pod. The previous ready Pod can remain during the rolling update. Inspect the failing Pod with `describe pod POD_NAME`; identify the exact image reference in the event. Recover by reapplying the declared source:

```bash
./scripts/lab.sh deploy
./scripts/lab.sh kubectl -n onboarding-demo logs deployment/status --tail=20
```

Explain why the old Pod could still serve requests, and why a healthy node alone does not establish a successful rollout. If you change ConfigMap values used as environment variables, remember existing processes do not reread them: restart the Deployment or use a generated ConfigMap name/checksum mechanism. [Kustomize documentation](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) covers declarative composition.

## Keep or clean up

Continue to [lab 04](../04-flux/README.md) while this cluster and imported toy image exist. To remove it later, stop any port forwards, uninstall Flux using lab 04 if installed, then run:

```bash
./scripts/lab.sh delete
```

Deletion checks recorded container IDs and removes only this cluster and registry. It retains the toy image in Docker and does not run a prune. Registry contents and cluster state are disposable. A partially failed creation may leave incomplete ownership records; inspect `k3d cluster list`, `k3d registry list`, and the named containers before any manual cleanup. Do not delete a replacement cluster just because it has the same name. Keep credentials out of screenshots and notes.

Useful next reading: [K3s architecture](https://docs.k3s.io/architecture), [k3d creation flags](https://k3d.io/v5.9.0/usage/commands/k3d_cluster_create/), [k3d registry networking](https://k3d.io/stable/usage/registries/).
