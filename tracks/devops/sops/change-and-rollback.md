# SOP: change and rollback

**Trigger:** change an image, configuration, platform resource, or dependency. **Success:** desired state and observed behavior agree, with a tested recovery decision.

## Before the change

1. Identify the owner: Compose, Terraform, Flux, another controller, or a supervisor. Confirm the disposable lab/context and current source revision. Check for unrelated local edits.
2. State the intended behavior and scope. List resource replacements/deletions, storage effects, secret changes, and any backwards-incompatible data changes.
3. Preserve the current usable artifact and relevant data. An old image digest is insufficient if its registry entry was deleted or the new schema cannot be read by it.
4. Validate the relevant artifact: Compose configuration, Terraform format/validation/plan, Kubernetes rendering and server validation where available. Review the actual change rather than assuming a generated file is safe.
5. Write the rollback trigger and verification before applying. In a personal lab, this is your own review; team approval requirements are not simulated by pretending someone approved.

## Apply and observe

Apply only the intended change using its owner. Check rollout/reconciliation conditions and the original synthetic request. Compare version/configuration and resource use with expectations. If behavior is wrong, stop further rollout and use the recovery path.

For GitOps, prefer reverting the desired-state commit and allowing reconciliation to converge. A direct `kubectl` edit can be overwritten. Temporary suspension needs an explicit resumption step and a final check. For Terraform, reverting configuration produces a **new plan**; it is not automatic undo. Review replacements and data effects before applying it. Kubernetes rollout undo does not reverse external secrets, database migrations, or arbitrary configuration changes.

```text
Intent / scope:
Lab / context / current revision:
Resource owner:
Proposed artifact / rendered diff / plan:
Validation performed and result:
Expected observation / observation window:
Rollback trigger:
Recovery artifact and data compatibility:
Action taken:
Observed behavior / final revision:
Any suspended controller resumed and checked:
```

Practice: change a toy response or image reference, predict the outcome, observe it, and recover to the previous response. Use no customer data. References: [Terraform workflow](https://developer.hashicorp.com/terraform/intro), [Flux concepts](https://fluxcd.io/flux/concepts/), and [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/).
