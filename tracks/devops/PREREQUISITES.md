# A local lab environment

## Choose a path

The recommended environment is your own disposable Ubuntu 24.04 LTS VM, or a comparable supported Linux installation, with Docker Engine and the Compose plugin. Use a local hypervisor you already trust. Give the VM NAT networking; do not bridge it onto a public network or open inbound router ports. A snapshot before installing tools makes reset easy.

Suggested comfortable allocation: **4 virtual CPUs, 8 GiB RAM, and 25 GiB free disk**. These are planning estimates for the whole lab path, not vendor minimums. Containers and Terraform alone need much less. Run one lab at a time if resources are limited. An existing computer is sufficient; do not rent a VM.

On macOS or Windows, either use a Linux VM or an eligible Docker Desktop installation. Windows commands in these guides run inside a Linux environment such as WSL2, with a working Docker connection. On Apple Silicon, use arm64 binaries and native multi-architecture images. Docker Desktop licensing depends on use and organization size; the Linux Engine path avoids a Desktop subscription dependency. [Docker Engine installation](https://docs.docker.com/engine/install/), [Docker Desktop terms](https://docs.docker.com/subscription/desktop-license/), and [Ubuntu Server installation](https://ubuntu.com/tutorials/install-ubuntu-server) explain those choices.

## Tools

Install only tools needed for the lab you choose. Use the official installation pages and release checksums/signatures, selecting your OS and CPU architecture. No installer is run automatically by this repository. Do not paste a remote install script into a root shell without reviewing it.

| Tool | Needed for | Selection |
| --- | --- | --- |
| Bash, Git, curl, Python 3 | General work, verification, toy app | Python 3.12 or newer |
| Docker Engine / CLI + Compose plugin | Labs 1, 3, 4 | A supported stable Engine and Compose v2+ command syntax (`docker compose`) |
| Terraform CLI | Lab 2 | 1.6 or newer within 1.x; validation here used 1.16.5 |
| k3d | Labs 3–4 | v5.9.0 |
| kubectl | Labs 3–4 | v1.35.x for the pinned K3s 1.35 lab |
| Flux CLI | Lab 4 | v2.9.4 |
| jq | Labs 3–4 helpers | Available from the OS package manager |
| SOPS and age / age-keygen | Lab 5 only | Tested with SOPS 3.13.3 and age 1.3.2 |

The cluster lab pins K3s `v1.35.9-k3s1`. These are reproducible teaching selections, not a promise that every version is the newest release or an instruction to downgrade an existing machine. Use a disposable VM to keep separate tool versions when needed. See [references](../../REFERENCES.md) for official install and release pages. Keep kubectl within its [supported version skew](https://kubernetes.io/releases/version-skew-policy/) from the API server.

For Ubuntu, the distribution packages can supply the basic utilities:

```bash
sudo apt-get update
sudo apt-get install git curl python3 jq ca-certificates
```

Install Docker Engine **and its Compose plugin** using Docker's distribution-specific guide. Terraform, k3d, kubectl, Flux, and SOPS have their own official release/install instructions. Check your downloaded release before adding it to `PATH`; the guides below do not silently install system packages.

## Verify your environment

Read the commands first. These report information and do not start lab resources:

```bash
git --version
python3 --version
docker version
docker compose version
docker context show
terraform version
k3d version
kubectl version --client
flux version --client
jq --version
```

Run the optional tool checks only for installed tools. `docker version` should report a reachable local server as well as a client. Check `docker context inspect` and make sure you selected your own local Engine; a Docker context can point to a remote host. Do not weaken socket permissions to fix an access error. Docker daemon access has powerful host privileges; follow the [Docker post-install guide](https://docs.docker.com/engine/install/linux-postinstall/).

Inspect existing containers and listeners before starting a lab:

```bash
docker ps --format 'table {{.Names}}\t{{.Ports}}\t{{.Status}}'
ss -ltn
```

`ss` is a Linux command; use your OS equivalent outside the VM. The examples use **18080** for Compose, **16443** for the Kubernetes API, **15100** for the local registry, **18083** for the direct Kubernetes service, and **18084** for the Flux-managed service. All host listeners bind to `127.0.0.1`. If a port is occupied, identify the owner and stop or reconfigure your own lab deliberately; do not kill an unrelated process.

## Work in the right directory

Unpack a supplied archive, or use a local copy of this repository. GitHub membership is unnecessary. Open a terminal at the directory containing the root `README.md`:

```bash
python3 scripts/verify.py
```

Lab scripts select their own kubeconfig, context, namespace, and resource names. Do not substitute a company kubeconfig. Run lab commands in a fresh shell if you have cloud credentials or production contexts configured elsewhere. The `.gitignore` keeps local state and credentials out of normal commits; it cannot prevent an explicit `git add -f`.

## Finish a session

Follow each lab's cleanup instructions. Compose `down` removes its containers and network; adding `--volumes` also destroys its synthetic volume. Deleting the k3d lab cluster removes its in-cluster data; the local registry has separate cleanup. Terraform `destroy` removes its state-managed lab objects. Deleting a VM is the simplest complete reset when it contains only these disposable exercises.

Initial image and binary downloads require public internet access. Once cached, some exercises work offline; this is not a fully air-gapped distribution. No paid AI API or hosted registry is needed.
