# SOP: patching and dependency updates

**Trigger:** a supported version update, vulnerability advisory, or end-of-support notice. **Success:** the selected layer is updated, essential behavior works, and recovery remains possible.

## Procedure

1. Inventory the affected layer: VM OS/kernel, container runtime, Kubernetes/K3s, Flux/controllers, image base, application dependency, or database. A clean application dependency scan says nothing about an unpatched host kernel.
2. Read the upstream advisory and release/upgrade notes. Identify affected versions, exposure, prerequisites, API removals, datastore compatibility, and whether a reboot is required. Record uncertainty instead of treating every finding as confirmed exploitability.
3. Pin the intended version or digest and retain the previous recoverable artifact. Preserve relevant data using a verified backup method. Database downgrade is not automatically supported.
4. Change one layer in the disposable environment. Review manifest diffs, Terraform plans, dependency lockfile changes, and permission changes as applicable. An automated update is still a change that needs observable validation.
5. Check startup, health/readiness, a synthetic workflow, controller convergence, and resource behavior. Record actual tool results; unavailable checks remain unverified.
6. Recover if the defined trigger is met. Reverting a controller image cannot undo every CRD or storage-format migration. Follow upstream recovery guidance when compatibility changed.
7. Record the final observed version, validation, remaining findings, and any required future action. Update pinned lab artifacts and documentation together when maintaining this repository.

## Supply chain questions

Can you trace source revision to image digest? Are dependencies locked? Is a downloaded binary from the publisher, and can its checksum/signature be verified? Does a controller require broad cluster permissions? Is a registry retention rule removing your rollback artifact? These questions apply even when the local lab incurs no service charges.

```text
Component / old version / proposed version:
Advisory or upstream release notes:
Exposure and compatibility considerations:
Backup / prior artifact:
Change / validation result:
Observed final version:
Recovery decision / remaining uncertainty:
```

References: [K3s upgrades](https://docs.k3s.io/upgrades), [Flux upgrade guide](https://fluxcd.io/flux/installation/upgrade/), and the [change procedure](change-and-rollback.md).
