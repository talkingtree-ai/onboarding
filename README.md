# Onboarding

An optional, self-paced introduction to technologies relevant to TalkingTree engineering. The **DevOps track** is ready to explore; product and software development tracks are placeholders.

Use this material on your own computer or a disposable local VM. No company GitHub membership, credentials, infrastructure access, customer data, paid API, or cloud account is required for the core path. The examples are original teaching projects with synthetic data. The architecture guide describes technology categories, rather than company deployment instructions.

This is optional self-study material with no deadlines, submissions, or requests to perform company work. Formal company access and onboarding follow separate processes.

## Start here

1. Choose the [DevOps track](tracks/devops/README.md).
2. Read the [local environment guide](tracks/devops/PREREQUISITES.md).
3. Follow the labs in order, or pick a topic you want to understand.
4. Keep any personal notes, keys, generated state, and backups in ignored `.local/` directories.

| Track | Status | Contents |
| --- | --- | --- |
| [DevOps](tracks/devops/README.md) | Available | Linux, networking, containers, Terraform, K3s, Flux, secrets, identity, data, and operations |
| [Product](tracks/product/README.md) | Planned | Product context and discovery |
| [Development](tracks/development/README.md) | Planned | Frontend, backend, integrations, and mobile |

## What you can build

The practical path starts with a tiny Python HTTP service, runs it in Docker Compose, explores Terraform's local state lifecycle, then deploys the service into a single-node K3s cluster using k3d. Flux reconciles versioned manifests from a local OCI registry, so the GitOps exercise needs no hosted Git repository. A separate SOPS/age exercise teaches encryption with locally generated disposable keys.

The [Traefik and local DNS lab](tracks/devops/labs/07-routing-dns/README.md) adds host-based reverse proxy routing, a private `.test` DNS zone, record changes, failure diagnosis, and optional local HTTPS. No domain purchase, external DNS service, company domain, or system resolver change is needed.

The default local stack is intentionally small. K3s in Docker teaches Kubernetes behavior; it does not reproduce a production cluster's hosts, networking, high availability, or security boundaries. Terraform's core lab manages local state objects and creates no cloud resources. Read the [technology map](tracks/devops/docs/architecture.md) for those distinctions.

## Cost and accounts

Reading and the core labs require no service subscriptions. Downloads need an internet connection and consume local disk, memory, and electricity. A Linux VM with Docker Engine is the recommended path. Check licensing if choosing Docker Desktop. Auth0 is an optional personal-tenant exercise; check its current plan terms before signing up, and skip it if you prefer to create no accounts. No credit card or cloud free-tier trial is part of the core path.

## Reference and maintenance

- [Public documentation directory](REFERENCES.md)
- [Sharing and contribution guidance](CONTRIBUTING.md)
- [Lab safety and credential handling](SECURITY.md)
- [Validation record and limitations](VALIDATION.md)

All commands assume the repository root unless a lab tells you to change directories. The lab guides include expected results, troubleshooting, and scoped cleanup. A local static check is available with `python3 scripts/verify.py`; it does not start containers, contact a cluster, or provision resources.
