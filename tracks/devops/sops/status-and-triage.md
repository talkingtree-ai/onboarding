# SOP: status and triage

**Trigger:** a lab endpoint fails, behaves slowly, or does not match desired state. **Success:** identify the failing boundary and verify the recovered observable behavior.

## Procedure

1. Confirm the lab identity: directory/project name, Kubernetes context if relevant, and expected service/port. Check what is already running. A port conflict is a diagnostic clue, not a reason to start a second copy on another port.
2. Define the symptom precisely: request path, UTC time, expected status/body, actual status/body, and whether the problem is reproducible. Use a bounded request timeout. Exclude authorization headers and sensitive query strings from notes.
3. Check host capacity, listeners, container or process ownership, workload status, and recent events. In Kubernetes, distinguish Pending, image pull failure, crash/restart, and unready workloads. Look at previous logs when a container restarted.
4. Follow the dependency path from client inward: DNS → connection → TLS → proxy route → service endpoints → application → dependency. A green proxy health endpoint proves only its own check.
5. Form one testable hypothesis. Collect the smallest diagnostic that could disprove it. Do not restart all dependencies, delete persistent storage, or disable authentication to see if the symptom disappears.
6. Choose a scoped fix or the [incident procedure](incident-response.md). Change one thing, then repeat the original failing operation and inspect adjacent effects. A successful restart command is not recovery evidence.

## Diagnostic prompts

| Observation | Next useful check |
| --- | --- |
| Connection refused | Expected address/port, listener ownership, stopped process |
| Timeout | Routing/firewall, saturation, dependency waits, resource pressure |
| Proxy 502 | Backend availability and selected route, not only proxy uptime |
| 401 / 403 | Intended token/session, audience, expiry, permissions, ownership checks |
| Healthy Pod, failed request | Service selectors/endpoints, route, application and dependency behavior |
| GitOps object unready | Source revision, fetch/render/apply/health conditions, controller events |

```text
Lab / context:
UTC start:
Expected / observed:
Affected boundary:
Hypothesis / disconfirming test:
Change made (if any):
Observed result:
Remaining uncertainty:
```

References: [Kubernetes application troubleshooting](https://kubernetes.io/docs/tasks/debug/debug-application/) and [Flux troubleshooting](https://fluxcd.io/flux/cheatsheets/troubleshooting/).
