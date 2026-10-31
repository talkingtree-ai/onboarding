# Linux, networking, storage, and observability

Use a disposable local lab or VM. Commands here are diagnostic examples; select only the tools and lab resources you actually installed. Keep notes locally if useful. Nothing needs to be submitted.

## Read a request as a sequence of boundaries

1. **DNS:** a name resolves to an address. A correct address does not prove a listener exists.
2. **TCP:** a listener accepts a connection on an address and port. Timeout, refusal, and DNS failure are different observations.
3. **TLS:** the client verifies the server name, trust chain, and certificate lifetime. Do not use disabled verification as a permanent fix.
4. **HTTP routing:** a proxy chooses a backend from the host and path. A proxy's 502 can coexist with a healthy backend reached through a different path.
5. **Application authorization:** a valid login does not grant access to every record.
6. **Dependencies:** a running API can still fail when data storage, signing keys, or a downstream service is unavailable.

`localhost` refers to the network namespace making the request. Inside a container it usually means that container; inside a VM it means the VM. Compose service names resolve on their Compose network. Kubernetes Service names resolve in cluster DNS. Host published ports are another boundary.

For a local service, publish explicitly to loopback and check the actual listener. [Docker's port publishing documentation](https://docs.docker.com/engine/network/port-publishing/) explains why an omitted host address can expose a port on every host interface. VM NAT and firewall configuration matter too; loopback inside the VM is not host loopback.

## Diagnose before restarting

These examples do not start services or change settings:

```bash
date -u
uname -sr
ss -ltnp
free -h
df -h
df -i
docker ps
docker stats --no-stream
```

Some process details require permission; missing details are not proof that a listener has no owner. `df -i` checks inode exhaustion, which can prevent writes while byte capacity remains available. `free`'s available memory is more useful than treating all filesystem cache as unavailable RAM.

Before any Kubernetes command, verify the lab's explicit kubeconfig, context, and endpoint. From lab 03's directory, use `bash scripts/lab.sh kubectl config current-context` and `bash scripts/lab.sh kubectl cluster-info`; the wrapper verifies the recorded local cluster before contacting it. Then inspect workloads, events, container restart counts, readiness, and logs through the same wrapper. A namespace alone does not guarantee you selected a disposable cluster.

For a service you created in a systemd VM, `systemctl status <lab-unit>` and `journalctl -u <lab-unit> --since '15 minutes ago'` help relate lifecycle and logs. Substitute a known lab unit; do not guess at host service names. A process in a shell and a supervised service have different lifecycle and resource boundaries.

## Resource controls describe different things

| Signal or setting | Meaning | Useful follow-up |
| --- | --- | --- |
| CPU utilization | Work being executed over an interval | Is latency caused by saturation or by waiting? |
| CPU request / limit | Scheduling reservation / runtime enforcement | Check throttling as well as average usage |
| Memory request / limit | Scheduling input / enforced container memory boundary | Check OOM termination reasons and peak working set |
| systemd `MemoryHigh` / `MemoryMax` | Reclaim pressure threshold / hard boundary | Inspect cgroup events, pressure, and the process before changing limits |
| Disk utilization and latency | Capacity and I/O service behavior | Check both bytes/inodes and I/O waits |
| Restart count | Lifecycle failures or restarts | Read previous container logs before evidence disappears |

Requests are not guarantees of application performance. A workload may stall under memory reclaim before it is killed. Raising a limit changes the budget available to other workloads. See [Kubernetes resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) and [systemd resource control](https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html).

## State survives only where designed

An image contains a packaged filesystem. A running container adds a writable layer; recreating the container discards that layer. A volume or PersistentVolume has a separate lifecycle. Node-local storage can survive a Pod replacement while still being lost with its node. A snapshot on the same disk is not protection from that disk failing.

Ask which component is authoritative. A cache might be rebuildable, but a queue or session store may carry information that cannot simply be discarded. Vector indexes may be rebuildable only if original documents, model/version information, metadata, and a deterministic reindexing process survive.

## Observe outcomes at several levels

Use a small number of meaningful signals: request success rate, latency percentiles, traffic, saturation, dependency errors, and backup age. Distinguish:

- **Liveness:** should this process be restarted?
- **Readiness:** can this instance receive traffic now?
- **Synthetic workflow:** can a user complete a small authorized operation?
- **Reconciliation health:** has the desired configuration actually converged?

A liveness probe that depends on every downstream service can create restart cascades. A synthetic check should use synthetic records, clean up afterward, and avoid storing tokens in results. Uptime Kuma is an example of [self-hosted availability monitoring](https://github.com/louislam/uptime-kuma). Fluent Bit's [pipeline model](https://docs.fluentbit.io/manual/concepts/data-pipeline) helps explain log inputs, filtering, buffering, and outputs. Logs need retention and redaction; collecting more data is not automatically better visibility.

Try this locally: stop only the toy application, inspect the symptom, and predict which checks remain green. Restart it through the lab's supported command and verify the observable outcome. For cluster failures, use the official [application troubleshooting guide](https://kubernetes.io/docs/tasks/debug/debug-application/).
