# Lab 07 — Traefik, private DNS, and local TLS

**Time:** 60–90 minutes, plus optional TLS. **Cost:** local compute and public
image downloads; no paid service, credit card, domain purchase, or online account.
Use your own machine or disposable VM with Docker, Compose v2 or newer, curl, and `dig`
(usually `dnsutils` or `bind-utils` on Linux). Optional TLS needs OpenSSL.
Allow about 1 GiB of free disk; the four containers have a combined 512 MiB
memory ceiling. This lab does not need a Kubernetes cluster.

You will operate an authoritative DNS zone, route two hostnames through Traefik,
diagnose failures at different layers, and optionally serve HTTPS with a local
certificate. All names are under `onboarding.test`, reserved for testing. The
zone is private to this lab; neither a registrar nor a public DNS provider is
involved. There is no access to company domains, infrastructure, or accounts.

```text
dig -> 127.0.0.1:15353 -> CoreDNS authoritative zone

curl --resolve -> 127.0.0.1:18085 -> Traefik -> notes:8080 or status:8080
                   optional :18443 HTTPS   -> same synthetic backends
```

DNS chooses an address. Traefik uses the HTTP `Host` value to choose a backend.
TLS, when enabled, adds certificate selection using SNI and certificate hostname
verification. These are separate steps; one succeeding does not prove the others.

## 1. Inspect and start

Run from this directory on your own lab machine. Inspect existing projects and
check that TCP ports 18085, 18443, 15353 and UDP port 15353 are free:

```bash
docker version
docker compose version
docker compose ls
docker compose ps -a
```

On Linux, use `ss -ltnp` and `ss -lunp`; on macOS, use `lsof -nP -iTCP -sTCP:LISTEN`
and `lsof -nP -iUDP:15353`. Identify any listener before continuing. Reuse your
existing lab project where appropriate; do not stop an unfamiliar process.

Read `compose.yaml`, `traefik/`, and `dns/`, then run:

```bash
docker compose config --quiet
docker compose build
docker compose up -d --wait --wait-timeout 90
docker compose ps
```

The project name is `onboarding-routing`. Only Traefik and CoreDNS publish host
ports, all bound to `127.0.0.1`. Backends are reachable only inside this project's
internal network. The proxy also joins a regular bridge so Docker can publish
its loopback host ports; DNS joins that bridge alone. Containers run as UID/GID
10001, drop capabilities, use read-only root
filesystems, and have CPU, memory, and process limits. CoreDNS alone retains
`NET_BIND_SERVICE` because its official binary carries that file capability;
dropping it from the bounding set can prevent the executable from starting,
even though this lab listens on high port 1053. No Docker socket,
dashboard, public tunnel, or recursive DNS forwarding is enabled. Process and
container health are preliminary checks; verify responses below.

## 2. Query a real local DNS zone

These commands query the lab's authoritative server explicitly. They do not
change your machine's DNS configuration or `/etc/hosts`.

```bash
dig @127.0.0.1 -p 15353 notes.onboarding.test A +norecurse
dig @127.0.0.1 -p 15353 status.onboarding.test A +norecurse +noall +answer
dig @127.0.0.1 -p 15353 www.onboarding.test CNAME +norecurse +noall +answer
dig @127.0.0.1 -p 15353 _verification.onboarding.test TXT +norecurse +noall +answer
dig @127.0.0.1 -p 15353 onboarding.test NS +norecurse +noall +answer
dig @127.0.0.1 -p 15353 onboarding.test SOA +norecurse +noall +answer
dig @127.0.0.1 -p 15353 absent.onboarding.test A +norecurse +noall +comments +authority
dig @127.0.0.1 -p 15353 notes.onboarding.test A +tcp +norecurse +noall +answer
```

Expected:

| Query | Result |
| --- | --- |
| `notes` and `status` A | `127.0.0.1`, TTL 60 |
| `www` CNAME | `notes.onboarding.test.` |
| `_verification` TXT | `"onboarding-lab-only-v1"` |
| Zone NS | `ns.onboarding.test.` |
| Zone SOA | Serial `2026103001` and timing fields |
| `absent` A | `NXDOMAIN`, with SOA in the authority section |
| TCP A lookup | Same answer as UDP |

The `aa` flag means the answer is authoritative. `+norecurse` avoids requesting
recursion from this authoritative-only server. The zone also gives `ns` and the
apex an A record. Its addresses are intentionally loopback; they are useful
only when queried and used on the same host as the Docker published ports.

## 3. Route HTTP by hostname

```bash
curl --noproxy '*' --fail --max-time 5 \
  --resolve notes.onboarding.test:18085:127.0.0.1 \
  http://notes.onboarding.test:18085/version
curl --noproxy '*' --fail --max-time 5 \
  --resolve status.onboarding.test:18085:127.0.0.1 \
  http://status.onboarding.test:18085/version
curl --noproxy '*' -i --max-time 5 \
  --resolve unknown.onboarding.test:18085:127.0.0.1 \
  http://unknown.onboarding.test:18085/version
```

Expected: the known names return HTTP 200 with different `message` values
(`Notes backend` versus `Status backend`); the unknown name returns Traefik's
HTTP 404. The two backend instances share original training code and contain no
real user data or authentication.

`--resolve` supplies curl's address mapping directly: these HTTP requests
**bypass DNS** and do not query CoreDNS. `--noproxy '*'` keeps the request local
even if your shell has an outbound HTTP proxy configured. To connect the DNS
result to the HTTP request explicitly:

```bash
lab_ip="$(dig @127.0.0.1 -p 15353 notes.onboarding.test A +norecurse +short)"
test "$lab_ip" = "127.0.0.1" || { printf '%s\n' 'Unexpected lab address'; exit 1; }
curl --noproxy '*' --fail --max-time 5 \
  --resolve "notes.onboarding.test:18085:$lab_ip" \
  http://notes.onboarding.test:18085/version
```

This explicitly queries DNS and then supplies the returned address to curl.
It still does not install CoreDNS as your operating system's resolver.

Trace the configuration: `traefik/static.yaml` defines the listening entrypoint
and file provider; `traefik/dynamic/http.yaml` defines Host routers and backend
services. Docker's internal service-name resolution supplies `notes` and
`status` to Traefik. That is separate from the learner-facing CoreDNS zone.

## 4. Domain-management exercises

Keep a short change record with the intended result, old/new values, validation,
and rollback. Use synthetic data only.

1. In `dns/db.onboarding.test`, change `$TTL 60` to `$TTL 15` and increase the SOA
   serial to `2026103002`. CoreDNS checks for a higher serial every five seconds.
   Query A and SOA again until the new TTL and serial appear. Observe that direct
   authoritative queries show the configured TTL; there is no caching resolver
   in this lab, so this does not demonstrate a cache counting down.
2. Change the verification TXT value to `onboarding-lab-only-v2`, increase the
   serial again, and query TXT. This models editing a domain-verification record;
   no external service is validating ownership. Restore `v1` with another higher
   serial. A rollback restores the old value with a **newer** serial.
3. Query `www` as both CNAME and A, then run:

   ```bash
   dig @127.0.0.1 -p 15353 www.onboarding.test A +norecurse +noall +answer
   curl --noproxy '*' -i --max-time 5 \
     --resolve www.onboarding.test:18085:127.0.0.1 \
     http://www.onboarding.test:18085/version
   ```

   DNS follows the CNAME to the same loopback address, but HTTP returns 404.
   A CNAME does not rewrite the HTTP Host value. Add a `www` router below the
   existing routers in `traefik/dynamic/http.yaml`:

   ```yaml
   www:
     entryPoints: [web]
     rule: "Host(`www.onboarding.test`)"
     service: notes
   ```

   Indent it to match the existing router entries. Wait a few seconds and repeat
   curl: expect HTTP 200 from `notes`. The watched directory allows this routing
   change without recreating the proxy. Remove the temporary router and verify
   404 again. If your filesystem does not deliver file-watch events, inspect the
   logs and recreate only `proxy`; do not restart the Docker daemon.
4. Restore the default TTL to 60 using a higher serial. Describe a real cutover:
   lower TTL sufficiently ahead of time for previously cached answers to expire,
   verify the replacement target, change the record, monitor old and new targets,
   and keep a rollback window. Lowering TTL does not erase existing caches.

Finish with a paper delegation drill. Sketch:

```text
registrant -> registrar -> registry/parent zone NS delegation
client -> recursive resolver -> parent -> authoritative nameserver -> record
```

Explain the registrar account versus DNS hosting, the role of an NS record and
in-bailiwick glue, domain renewal, and who owns change approval and recovery.
Our private zone's NS record is real DNS data, but no public parent delegates
`onboarding.test` to this server. Registrar transfers, public propagation,
DNSSEC chains, and public ownership validation are discussion topics here.
This approach exercises DNS administration without a purchased domain or
someone else's domain access.

## 5. Diagnose a proxy failure

Stop just the synthetic notes backend:

```bash
docker compose stop notes
curl --noproxy '*' -i --max-time 5 \
  --resolve notes.onboarding.test:18085:127.0.0.1 \
  http://notes.onboarding.test:18085/version
curl --noproxy '*' --fail --max-time 5 \
  --resolve status.onboarding.test:18085:127.0.0.1 \
  http://status.onboarding.test:18085/version
dig @127.0.0.1 -p 15353 notes.onboarding.test A +norecurse +noall +answer
docker compose ps -a
docker compose logs --tail 20 proxy notes
docker compose up -d --wait --wait-timeout 60 notes
curl --noproxy '*' --fail --max-time 5 \
  --resolve notes.onboarding.test:18085:127.0.0.1 \
  http://notes.onboarding.test:18085/version
```

Expected with this file-provider configuration: notes returns HTTP 502 while
stopped, status remains HTTP 200, DNS remains valid, and notes returns HTTP 200
after recovery. The file provider retains its configured backend while Docker
health does not remove it from Traefik's routing configuration. A configuration
with active upstream health checks can instead return 503 when no server is
available. Record the actual response and inspect the affected layer.

## 6. Optional local HTTPS

Run this after restoring the default HTTP configuration above. This extension
adds an HTTPS listener using a seven-day self-signed certificate with SANs for
the two known hostnames. It makes no ACME request, installs no system root, and
changes no browser or operating-system trust settings.

```bash
./generate-cert.sh
openssl x509 -in .local/certs/local.crt -noout -subject -dates -ext subjectAltName
docker compose -f compose.yaml -f compose.tls.yaml config --quiet
docker compose -f compose.yaml -f compose.tls.yaml up -d --wait --wait-timeout 90
curl --noproxy '*' --fail --max-time 5 \
  --cacert .local/certs/local.crt \
  --resolve notes.onboarding.test:18443:127.0.0.1 \
  https://notes.onboarding.test:18443/version
curl --noproxy '*' --fail --max-time 5 \
  --cacert .local/certs/local.crt \
  --resolve status.onboarding.test:18443:127.0.0.1 \
  https://status.onboarding.test:18443/version
```

Expected: both HTTPS requests return HTTP 200 and retain their distinct backend
messages. For a trust failure, repeat one request without `--cacert`: curl
should reject this untrusted self-signed certificate. For a name mismatch, use
`--cacert` with `--resolve wrong.onboarding.test:18443:127.0.0.1` and request
`https://wrong.onboarding.test:18443/version`; certificate validation fails before
an HTTP response. Do not use `-k` to suppress the evidence.

The overlay replaces the static and dynamic configuration mounts with `tls/`
versions and adds only loopback port 18443; HTTP remains available. The toy
private key stays in ignored `.local/`, whose host parent directory is owner-only.
The key itself is readable inside the proxy's dedicated mount so non-root UID
10001 can use it. This key is disposable training material; never substitute
an organization certificate or reuse it for another purpose. The generation
script refuses to overwrite an existing pair.

Explain where TLS terminates, why the upstream remains HTTP on the isolated
network, what SNI selects, and how SAN verification differs from HTTP routing.
Public ACME issuance requires a publicly valid name and successful control
validation; this reserved private zone is not a public certificate workflow.
The lab's CLI-only trust scope deliberately avoids system changes.

## Cleanup and completion

Inspect the project, then remove only this lab's containers and networks. The
same cleanup works whether or not TLS was enabled:

```bash
docker compose ps -a
docker compose down --remove-orphans
```

The lab has no named volumes. Keep or delete `.local/` deliberately after the
proxy is stopped; it contains only generated lab certificate material. Leave
the shared `onboarding-status:local` image if another lab uses it. No host DNS,
hosts-file, firewall, or trust-store reversal is needed. Avoid global prune.

You are done when you can explain the difference between DNS failure, unmatched
Host (404), unreachable upstream (502), and certificate verification failure;
perform and roll back a DNS record change with increasing SOA serials; and
show that both UDP and TCP DNS queries work. Follow the
[routing and domain guide](../../docs/routing-and-dns.md) for context.

## Public references

- [Traefik file provider and mounted-directory watching](https://doc.traefik.io/traefik/reference/install-configuration/providers/others/file/)
- [Traefik HTTP routers](https://doc.traefik.io/traefik/reference/routing-configuration/http/routing/router/)
- [Traefik services and upstream health checks](https://doc.traefik.io/traefik/reference/routing-configuration/http/load-balancing/service/)
- [Traefik TLS certificates and SNI](https://doc.traefik.io/traefik/reference/routing-configuration/http/tls/tls-certificates/)
- [Traefik v3.7.17 release](https://github.com/traefik/traefik/releases/tag/v3.7.17)
- [CoreDNS file plugin and serial-based reload](https://coredns.io/plugins/file/)
- [CoreDNS manual](https://coredns.io/manual/toc/)
- [CoreDNS v1.15.0 release](https://github.com/coredns/coredns/releases/tag/v1.15.0)
- [CoreDNS image's declared file capability](https://github.com/coredns/coredns/blob/v1.15.0/Dockerfile)
- [IETF special-use domain names, including `.test`](https://www.rfc-editor.org/rfc/rfc6761.html#section-6.2)
- [curl `--resolve`, `--cacert`, and `--noproxy`](https://curl.se/docs/manpage.html)
