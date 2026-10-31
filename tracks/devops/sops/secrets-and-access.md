# SOP: secrets and least privilege

**Trigger:** create, rotate, revoke, or review a lab credential. **Success:** only the intended identity can perform the intended operation, and old access is removed when required.

## Inventory authority

For each identity, record purpose, resource scope, allowed operations, expiration/review date, and revocation mechanism. Record identifiers only, not credential values. Separate human accounts, build identities, runtime identities, and controller identities. A registry read identity should not need infrastructure administration; an application should not need a cluster administrator's kubeconfig.

No company invitation, account, key, or access review is part of this track. Use your own sandbox, and avoid shared personal administrator credentials. A personal lab note is not evidence that a company control ran.

## Handle secrets

1. Use synthetic/disposable values for examples. Keep real sandbox secrets in ignored local files with restricted permissions or an appropriate local secret facility. Confirm the ignore rule before writing a file; ignoring it after committing does not remove history.
2. Keep credentials out of source, image layers, Docker build arguments, logs, screenshots, Terraform plans/state shared with others, and browser bundles. Marking a Terraform variable `sensitive` does not by itself prevent its value from being stored in state.
3. Treat Kubernetes Secrets as sensitive API objects. Base64 encoding does not encrypt them. RBAC, encryption at rest, workload access, and cluster-admin authority matter independently.
4. For encrypted Git material, understand both SOPS recipient configuration and custody of the age private identity. Keep the identity out of Git and preserve a separate recovery path. For External Secrets, scope the controller's external permissions and Kubernetes write permissions; synchronization is not a substitute for access control.

See [Terraform sensitive data](https://developer.hashicorp.com/terraform/language/manage-sensitive-data), [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/), [Flux SOPS](https://fluxcd.io/flux/guides/mozilla-sops/), and [External Secrets](https://external-secrets.io/latest/introduction/overview/).

## Rotate or revoke

Identify all consumers. Where the issuer supports overlapping credentials, create a replacement, update only intended consumers, verify successful access, revoke the old credential, and verify the old credential fails. Where overlap is unsupported, plan the interruption and recovery explicitly. Do not put either value in the rotation note.

If a secret reaches Git or another shared location, revoke/rotate it at its issuer first. Deleting the file or rewriting a commit cannot make an exposed credential safe. Check relevant issuer logs without collecting unnecessary personal information.

## Optional access drill

In your local cluster, reason about a namespaced read-only role that can inspect Pods but cannot read Secrets or create workloads. Use the lab's explicit context and `kubectl auth can-i` to test permitted and denied verbs for a dedicated lab identity. Administrator impersonation may require elevated rights; do not assume a successful administrator request tests the restricted identity. Remove the toy binding afterward.

```text
Identity identifier / type / purpose:
Allowed resource scope and operations:
Explicit denied operation tested:
Credential storage and expiry (no values):
Consumer update / verification:
Revocation result / old-access failure:
Remaining access / next review reason:
```
