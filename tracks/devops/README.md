# DevOps track

Explore how a small application moves from a local process to a reconciled Kubernetes workload, and how to operate it safely. Every exercise is optional. You can read the explanations without installing anything, and keep all notes to yourself.

## Learning path

| Step | Read or build | What to understand afterward |
| --- | --- | --- |
| 0 | [Prerequisites](PREREQUISITES.md), [architecture](docs/architecture.md), [foundations](docs/foundations.md) | Processes, sockets, HTTP, DNS, TLS, files, permissions, and the technology map |
| 1 | [Containers and Compose](labs/01-containers/README.md) | Build an image, run a non-root service, use health checks, inspect logs, and preserve synthetic data |
| 2 | [Terraform without cloud](labs/02-terraform/README.md) | Read a plan, track state, validate input, change resources, and destroy local lab state |
| 3 | [K3s with k3d](labs/03-k3s/README.md) | Deployments, Services, namespaces, Kustomize, probes, resource requests and limits |
| 4 | [Flux reconciliation](labs/04-flux/README.md), [delivery concepts](docs/delivery.md) | Source artifacts, reconciliation, drift correction, rollout, rollback, and pruning |
| 5 | [SOPS and age](labs/05-secrets/README.md), [secrets and access](sops/secrets-and-access.md) | Encryption, key custody, least privilege, and rotation |
| 6 | [Identity](docs/identity.md), [stateful services](docs/stateful-services.md) | Authentication versus authorization, persistence, caching, search, and restore strategy |
| 7 | [Operations capstone](labs/06-operations/README.md), [SOP library](sops/README.md) | Diagnose a failure, record a change, restore data, and explain evidence |
| 8 | [Traefik and local DNS](labs/07-routing-dns/README.md), [routing guide](docs/routing-and-dns.md) | Manage a private DNS zone, route hostnames, inspect TLS, and distinguish DNS, proxy, and backend failures |

Each lab stands alone where practical. Lab 4 reuses the cluster and image from lab 3. The secrets lab needs neither Kubernetes nor Auth0. Only the optional identity walkthrough uses a personal hosted account. Reading the full path can take a few evenings; installing and experimenting can take longer. There is no completion target.

Lab 7 uses standalone Compose and can follow the containers lab directly. Its reserved `.test` names, authoritative DNS server, and local certificate need no registered domain, public DNS account, or company domain access. You can practice without changing your computer's resolver or hosts file.

## Concepts worth practicing

Before applying a change, identify its owner, scope, source of truth, expected effect, and rollback. During an incident, distinguish observation from inference. A passing liveness check is weaker evidence than a successful authenticated user workflow. A backup is useful only when its restoration has been demonstrated.

Keep these boundaries in mind:

- A container is a process isolation mechanism and shares its host kernel. A disposable VM provides a separate host boundary.
- k3d uses Docker to run K3s nodes. The workload runtime inside K3s is containerd.
- Terraform and Flux own different desired state in these examples. Do not let both manage the same Kubernetes objects.
- Kubernetes Secrets are encoding and access-control objects; base64 is not encryption.
- A local artifact registry provides transport for the Flux exercise. A reviewed Git commit would normally provide change history in a fuller delivery pipeline.

## Local notes

Use `.local/notes.md` for observations if useful. Suggested prompts: What failed? What evidence narrowed the cause? Which change fixed it? How did you verify the outcome? What would differ in a multi-user production system?

No one needs these notes submitted. The [SOP templates](sops/README.md) are examples for practicing clear operational writing.
