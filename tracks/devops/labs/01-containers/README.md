# Lab 01 — Containers, health, and storage

**Time:** about 45–60 minutes. **Cost:** local CPU, disk, and image downloads;
no cloud subscription or account. Use a personal machine or disposable VM,
Docker Engine or another compatible local Docker setup, Compose v2 or newer, and curl.
Allow about 1 GiB of free disk. Follow the tool vendor's license terms; Docker
Engine on Linux is one local option. Windows users can use a Linux VM or WSL2.

You will build an image, run as a non-root user, compare liveness with readiness,
persist a synthetic note, restore a backup, and remove only this lab's resources.
The [toy application](../../../../examples/status-service/README.md) has no
third-party Python dependencies.

## 1. Inspect before starting

Run these commands from this directory. Check whether you already have a copy
of this project running and whether port 18080 belongs to another process:

```bash
docker version
docker compose version
docker compose ls
docker compose ps -a
```

On Linux, use `ss -ltnp 'sport = :18080'`; on macOS, use
`lsof -nP -iTCP:18080 -sTCP:LISTEN`. If another process owns the port, identify
it before proceeding. Never stop an unknown process just to make this lab run.
Docker access is powerful; use your own isolated environment and the vendor's
supported permission setup.

Read `compose.yaml` and the Dockerfile before running anything. The published
port binds to `127.0.0.1`; it is not intended for a public tunnel or shared host.
The container listens on all container interfaces so the loopback port mapping
can reach it. Those are different network namespaces.

## 2. Build and verify

```bash
docker compose config --quiet
docker compose build
docker compose up -d --wait --wait-timeout 60
docker compose ps
curl --fail http://127.0.0.1:18080/healthz
curl --fail http://127.0.0.1:18080/readyz
curl --fail http://127.0.0.1:18080/version
docker compose exec -T status id
```

Expected: the service becomes healthy, health says `alive`, readiness says
`ready`, version says `1.0.0`, and `id` reports UID/GID 10001. The first build
downloads a public Python image and may take several minutes. If Compose does
not support `--wait`, update to a supported Compose release or run
`docker compose up -d` and inspect `docker compose ps` until healthy.

Image metadata, declared ports, and a green process list are not end-to-end
proof. The curl checks demonstrate that the host can reach the running service.

## 3. Persistence and a restore drill

The named volume contains only this lab's synthetic note and maintenance flag.
`down` retains it; container replacement does not erase it.

```bash
docker compose exec -T status python /app/data_tool.py seed --text "First synthetic note"
curl --fail http://127.0.0.1:18080/note
mkdir -p backups
docker compose exec -T status python /app/data_tool.py backup > backups/note.json
docker compose exec -T status python /app/data_tool.py seed --text "A later synthetic note"
docker compose exec -T status python /app/data_tool.py restore < backups/note.json
curl --fail http://127.0.0.1:18080/note
docker compose down
docker compose up -d --wait --wait-timeout 60
curl --fail http://127.0.0.1:18080/note
```

Expected: the restored and restarted service returns `First synthetic note`.
This is an application-specific JSON backup of one small file. It excludes the
maintenance flag and is not a database-consistent snapshot or disaster recovery
system. A useful backup drill checks restored content, not just file existence.
The `backups/` directory is ignored by Git; use synthetic content only.

## 4. Break and diagnose

Turn off readiness while leaving the HTTP process alive:

```bash
docker compose exec -T status python /app/data_tool.py maintenance-on
curl --fail http://127.0.0.1:18080/healthz
curl -i http://127.0.0.1:18080/readyz
docker compose ps
docker compose logs --tail 20 status
docker compose exec -T status python /app/data_tool.py maintenance-off
curl --fail http://127.0.0.1:18080/readyz
```

Expected: liveness remains HTTP 200 and Docker health stays healthy, but
readiness returns HTTP 503 until the flag is removed. Docker does not route
traffic based on Kubernetes-style readiness. The later Kubernetes lab uses
separate probes for that purpose.

Try these small exercises, one change at a time:

- Change `APP_VERSION` to `1.0.1`, run `docker compose up -d`, then verify
  `/version`. Explain why merely editing the file does not change a container.
- Attempt `docker compose exec -T status touch /app/should-fail`. Explain the
  read-only filesystem failure; do not remove the guard to hide it.
- Inspect the resource limits with `docker inspect` or `docker stats --no-stream`.
  Explain why a container limit is different from reserving host memory.
- Stop the container, collect the evidence, and restart only `status`. Avoid
  changing several settings or restarting your entire Docker daemon.

Record symptoms, the layer you inspected, the smallest fix, and evidence that
the service recovered. Keep any learning notes local and free of credentials.

## Cleanup

Retain the note for a later session:

```bash
docker compose down
```

When finished with this disposable data, inspect the project and explicitly
remove only its containers, network, and declared volume:

```bash
docker compose ps -a
docker compose down --volumes --remove-orphans
docker image rm onboarding-status:local
```

The image removal may be refused if another lab still uses it; leave it until
that lab is stopped. Keep or delete `backups/note.json` deliberately. Never use
global prune commands as a substitute for project cleanup.

## Read more

- [Compose application model](https://docs.docker.com/compose/intro/compose-application-model/)
- [Compose service options](https://docs.docker.com/reference/compose-file/services/)
- [Compose up and health waiting](https://docs.docker.com/reference/cli/docker/compose/up/)
- [Docker volume lifecycle and backup concepts](https://docs.docker.com/engine/storage/volumes/)
- [Docker build best practices](https://docs.docker.com/build/building/best-practices/)
