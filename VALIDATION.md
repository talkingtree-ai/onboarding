# Validation record

Prepared on October 30, 2026. This record distinguishes checks that ran from optional exercises that still require the learner's own environment. The examples were written independently using public documentation; company source, secrets, and deployment configuration were not copied.

## Offline checks

- Python 3: six behavior tests covering HTTP response logic, readiness, synthetic backup/restore, invalid backup handling, oversized input, and missing routes. No network listener is opened by those tests.
- Docker Compose v5.6.0: configuration parsed successfully.
- Terraform v1.16.5: formatting, initialization, validation, plan, create, no-op plan, update, replacement, invalid input rejection, and destroy. All resources used the built-in provider and local state in a temporary directory.
- kubectl v1.35.9 / Kustomize v5.7.1: both direct and Flux-overlay manifests rendered successfully. Namespace rewriting was checked.
- Bash: script syntax, help output, missing-owner and target-override checks.
- Repository check: relative links, Markdown fences, Python/Bash syntax, and a small set of common credential patterns.

## Runtime checks

The local runtime path passed on Linux amd64 with Docker Engine, Compose v5.6.0, k3d v5.9.0, K3s v1.35.9+k3s1, kubectl v1.35.9, and Flux v2.9.4:

- Built the original image; verified HTTP liveness/readiness/version and UID/GID 10001 under Compose.
- Seeded synthetic data, backed it up, overwrote it, restored it, and verified content after container replacement. Maintenance returned readiness 503 while liveness stayed 200.
- Created the isolated cluster without updating the default kubeconfig, imported the toy image, deployed restricted Pods, and checked rollout and HTTP responses through loopback port forwarding.
- Installed the two Flux controllers, published manifests to the local OCI registry, reconciled them, and observed ready source/workload conditions.
- Corrected manual replica drift from three to one, promoted a second snapshot to two replicas, and rolled back to the retained one-replica snapshot. Verified the selected revision against its digest receipt and the Flux-managed service over HTTP.
- Uninstalled Flux with inventory pruning, then removed the lab containers, registry, volumes, network, and toy image tags. Cleanup order was corrected during verification and tested again separately.

SOPS v3.13.3 and age v1.3.2 passed both synthetic YAML encryption/decryption round trips, ciphertext inspection, isolated wrong-key rejection, and cleanup. Explicit YAML indentation was added after the initial byte-comparison check exposed reserialization differences. No real credential or existing key source was used.

Downloaded validation binaries were checked against upstream checksums or release asset digests. This is an integrity check, not a claim of independent signature or supply-chain verification. These are teaching configurations; no production readiness claim follows from a successful local check.

## Traefik and private DNS extension

Lab 07 was verified on Linux amd64 with Compose v5.6.0, Traefik v3.7.17, and CoreDNS v1.15.0. Both base and optional TLS Compose configurations parsed successfully. Live checks covered:

- Two hostname routes returning distinct synthetic backend responses; unmatched hosts and the unconfigured CNAME hostname returning 404.
- Authoritative A, CNAME, TXT, NS, and SOA answers; matching UDP/TCP lookups; NXDOMAIN for a missing name and NOERROR for an existing name without an AAAA record.
- Live TTL and TXT changes, serial-based zone reload, and rollback using a higher SOA serial.
- Adding and removing an HTTP hostname router through the watched file provider without recreating the proxy.
- A stopped backend returning 502 while the other route and DNS remained available, followed by recovery.
- HTTPS success for both SAN names using per-request certificate trust, plus rejection of an untrusted certificate and a hostname mismatch.
- Project-scoped cleanup of the four containers and both networks. Generated local keys/certificates were removed after testing, and the existing development stack remained healthy.

Testing corrected host-port publication by separating the internal backend network from the proxy/DNS bridge. CoreDNS retains its binary's declared `NET_BIND_SERVICE` capability to permit startup; other capability drops, non-root execution, and read-only roots remain configured. The lab documents this image-specific behavior. No public DNS record, company domain, default resolver, hosts file, or trust store was changed. The existing K3s/Flux runtime was unaffected and was not repeated for this extension.

## Public documentation site

The Pages release received an independent current-file and Git-history review,
plus Gitleaks scans of the source, staged Markdown, and generated website. No
actual secrets, private infrastructure identifiers, or proprietary source were
found. Current source and website scans reported zero findings; the historical
English-text false positive is documented in [the release review](PUBLIC-RELEASE.md).

The pinned documentation environment passed dependency checks and a strict build
of 32 reviewed source pages plus third-party notices. Rendered local links and
fragment anchors were checked. Browser verification covered the homepage, local
search results, navigation to a lab, code copying, and a narrow-screen navigation
drawer. The presentation uses original styles and public theme assets. No lab
runtime or shared application service was changed for the website work.

## Repeat relevant checks

From the repository root:

```bash
python3 scripts/verify.py
python3 -m unittest discover -s examples/status-service -p 'test_*.py'
docker compose -f tracks/devops/labs/01-containers/compose.yaml config --quiet
docker compose -f tracks/devops/labs/07-routing-dns/compose.yaml config --quiet
terraform -chdir=tracks/devops/labs/02-terraform fmt -check
kubectl kustomize tracks/devops/labs/03-k3s/manifests > /dev/null
kubectl kustomize tracks/devops/labs/04-flux/app > /dev/null
```

The Terraform README describes its complete local lifecycle. The container, K3s, Flux, and secrets guides describe live checks and cleanup; run them in a disposable environment if their runtime files change.

The [routing lab](tracks/devops/labs/07-routing-dns/README.md) describes its separate DNS, HTTP, and optional HTTPS checks. Generate its disposable certificate before validating or starting the TLS overlay.

## Limits

The optional Auth0 walkthrough is a documented exercise; no tenant or client was created during preparation. The stateful-services module is a design exercise rather than an installed database stack. CI, managed secrets, public edge services, public certificate issuance, cloud infrastructure, multi-node availability, real document processing, and paid AI integrations are reading topics only. They are not deployed by the labs. Lab 07's local reverse proxy, private DNS, and self-signed certificate are separate from those public services.

The integration environment is Linux amd64. macOS, Windows/WSL2, arm64, alternate Docker backends, and disconnected installations require separate verification. Lab resource limits constrain workloads but do not reserve capacity on the host. Upstream tags, release availability, and free-plan terms can change. Review dependencies and licensing before redistributing a revision.
