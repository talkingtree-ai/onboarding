# Lab 06 — Operate the toy service

Combine the earlier labs with the [SOP library](../../sops/README.md). Use only the synthetic service and your own local resources. These exercises are optional practice; no report, deadline, or evaluation is required.

## Scenario A: the process is healthy but the service is not ready

Start the [Compose lab](../01-containers/README.md) and run its maintenance drill. Before reading further, record the HTTP status for `/healthz` and `/readyz`, the container health status, and the resource usage.

Explain which observation establishes a live process and which establishes readiness. In Kubernetes, a failed readiness probe removes the Pod from normal Service endpoints; it does not itself restart the container. A failed liveness probe can trigger a restart. Use the [Kubernetes probe guide](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/) to check your explanation. Follow the [triage SOP](../../sops/status-and-triage.md), then remove the maintenance flag and verify recovery through HTTP.

## Scenario B: investigate an image that cannot start

Use the direct-deploy namespace from [lab 3](../03-k3s/README.md), before changing anything in the Flux-managed namespace. From lab 3's directory:

```bash
bash scripts/lab.sh kubectl -n onboarding-demo set image deployment/status \
  status=onboarding-status:deliberately-missing
bash scripts/lab.sh kubectl -n onboarding-demo get pods
bash scripts/lab.sh kubectl -n onboarding-demo get events --sort-by=.lastTimestamp
bash scripts/lab.sh kubectl -n onboarding-demo describe deployment status
```

Wait long enough to see image-pull failure events. An earlier replica may keep serving because Deployments use rolling updates. Distinguish deployment progress from user-visible availability. The image is fictional and is not expected to exist in a public registry.

Recover through the direct lab's source of truth:

```bash
bash scripts/lab.sh deploy
bash scripts/lab.sh kubectl -n onboarding-demo rollout status deployment/status
```

Port-forward and verify `/readyz` and `/version` as shown in lab 3. Capture the symptom, evidence, action, and verification using the [incident template](../../sops/incident-response.md). Do not relax probes or security settings to conceal the failure.

## Scenario C: a manual change keeps disappearing

Complete [lab 4](../04-flux/README.md), including its drift experiment. Explain why a manual replica change returns to the declared value. Publish a new local snapshot for an intentional change, select it, and verify the observed revision and application behavior. Roll back to the previous snapshot and verify again.

Prepare a local change record using the [change SOP](../../sops/change-and-rollback.md). Include the artifact revision, expected effect, checks, rollback trigger, and outcome. State why a direct `kubectl rollout undo` is temporary when Flux still declares a different state.

## Scenario D: restore after an accidental edit

Use the Compose lab's JSON backup workflow. Save a synthetic note, overwrite it, restore it, and compare the restored content. Replace the container and check persistence again. Record the observation time, backup scope, and the content comparison using the [restore SOP](../../sops/backup-and-restore.md).

Explain what is missing for a real database recovery plan: consistent snapshots or logical dumps, protected backup copies, retention, recovery point and recovery time objectives, restore dependencies, and access checks. A PVC, a volume, or a snapshot on the same lost disk does not by itself satisfy that plan.

## Scenario E: review a proposed change

Choose one lab change and review its diff locally. Identify any credential exposure, new host port, missing resource limit, mutable dependency, incorrect target context, or ambiguous ownership. Run the static checks and the relevant runtime checks. Keep suggested improvements as private notes, or implement them in a local branch for practice.

## Finish

Use the cleanup instructions in labs 1, 3, 4, and 5. If the Flux lab is running, uninstall its managed resources before deleting the cluster when you want to observe pruning. Delete only your recorded cluster and registry. There is no need for global Docker pruning or machine-wide process termination.
