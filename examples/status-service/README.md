# Synthetic status service

This original Python standard-library application exists for the learning labs.
It contains no company application code, integrations, accounts, or real data.

| Request | Result |
| --- | --- |
| `GET /healthz` | HTTP 200: the process can answer HTTP |
| `GET /readyz` | HTTP 200 if the data directory exists and maintenance is off; otherwise 503 |
| `GET /version` | Synthetic service name, version, and environment |
| `GET /note` | A synthetic note from local storage, or a placeholder |
| Other paths | HTTP 404 |

There are no HTTP write endpoints. `data_tool.py` changes the note and readiness
flag from a local CLI. Readiness is a teaching signal; it does not check a real
database or identity provider. The service has no authentication or TLS, so keep
it on loopback or inside an isolated training cluster.

Use the [container lab](../../tracks/devops/labs/01-containers/README.md) for a
guided build. To run without Docker on your own machine with Python 3.12+:

```bash
mkdir -p /tmp/onboarding-status
python3 app.py
```

It listens on `127.0.0.1:18080` and reads its disposable note under
`/tmp/onboarding-status`. Stop with Ctrl+C. To choose a private directory, set
`DATA_DIR` before starting and create the directory; do not point it at real
application data. `APP_VERSION`, `APP_ENV`, and `MESSAGE` customize the synthetic
version response. The HTTP process does not need write access to its data
directory; optional CLI exercises do.

The container uses UID/GID 10001. Its `/data` directory is writable; the Compose
lab makes the rest of the filesystem read-only. The Dockerfile uses a versioned
public [Python image](https://hub.docker.com/_/python), which still has a mutable
tag. For reproducible promotion, verify an image and pin its digest yourself.

Python's [`http.server`](https://docs.python.org/3/library/http.server.html) is
appropriate here as a small educational tool; use a maintained application
server and normal production controls for a real service.

Run the behavior checks from this directory with `python3 -m unittest -v`.
They exercise readiness and synthetic backup restoration without starting a
network listener.
