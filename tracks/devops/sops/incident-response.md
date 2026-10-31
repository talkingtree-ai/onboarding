# SOP: practice incident response

**Trigger:** a synthetic workflow is unavailable or incorrect. **Success:** restore the workflow, check integrity, and explain what happened without overstating certainty.

## Procedure

1. Record impact and start time. In a personal lab, you are the operator; there is no need to notify a company channel. For future team environments, use that environment's actual escalation and communication policy.
2. Stop unrelated changes. Capture selected logs/events, desired revision, image identity, and failure response before replacing a container or losing transient evidence. Sanitize the capture before saving it.
3. Use [triage](status-and-triage.md) to locate the failure. Classify availability, integrity, security, and resource exhaustion separately; a reachable service can still return incorrect data.
4. Choose the smallest recovery: correct a bad route, revert a known release, restore a failed dependency, or stop a runaway lab workload. Check that a reconciler will not immediately undo the recovery.
5. If credentials are exposed, revoke or rotate them through their issuer. Keep secret values out of the incident note. If a restore is needed, preserve the damaged source and restore elsewhere first.
6. Verify the original synthetic workflow, expected record/object consistency, readiness, restart counts, and sustained resource use. Check after at least one reconciliation interval when Flux is involved.
7. Write a short review separating observations from hypotheses. Choose a prevention improvement that addresses the causal chain; do not treat “restart faster” as the only lesson.

## A contained drill

Use the toy HTTP lab. Stop only its application container through the lab's Compose command, observe the failed request, and bring that service back through the same project. Do not delete volumes or affect unrelated containers. Optionally make a bad image reference in a lab manifest and practice a versioned revert. Inspect that the request works afterward rather than relying on a command's exit status.

```text
Impact / scope:
UTC timeline: symptom -> diagnosis -> action -> verified recovery
Facts observed:
Likely causes / unresolved hypotheses:
Recovery action and why selected:
Integrity checks:
Evidence retained (sanitized):
One prevention improvement:
```

Related reading: [Kubernetes debugging](https://kubernetes.io/docs/tasks/debug/debug-application/) and the [change and rollback procedure](change-and-rollback.md).
