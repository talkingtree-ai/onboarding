# Lab safety and credentials

Use only your own disposable local resources and synthetic records. Keep company accounts, source, manifests, customer documents, environment files, registry addresses, network maps, credentials, and audit evidence outside this repository and its history.

The lab app is intentionally small, with no authentication, and is not suitable for public hosting. Host ports bind to loopback. The optional local registry uses HTTP without authentication solely inside the local lab. Docker and k3d require significant host privileges; they are best run inside a disposable VM. A lab namespace is not a security boundary against a cluster administrator.

The routing lab uses reserved `.test` names and a local authoritative DNS container. It changes neither public records nor your system's default resolver. Its optional self-signed certificate is trusted only for the demonstrated curl request using `--cacert`; no root certificate is installed. Keep generated private keys under ignored `.local/`. No ACME account, DNS API token, or company hostname belongs in the lab.

Generate your own disposable keys when instructed. The `.local/` directory is ignored, but Git ignore rules are not access control. Use restrictive file permissions. Do not paste tokens, cookies, private keys, state files, or signed object URLs into logs or discussions. Never use a real credential as a teaching example.

If a credential reaches Git history, revoke or rotate it at the issuer and remove it from the distributed history before sharing. Deleting the current file does not erase earlier commits. For company secrets, follow the authorized internal incident process instead of experimenting here.

An optional Auth0 tenant belongs to the learner. Use no company tenant, branding, domain, or client registration. Account creation and current plan eligibility are the learner's choice. No login is required for the core labs.

For distribution, use a reviewed archive of tracked files rather than zipping a working directory containing `.local/`. The [maintainer guide](CONTRIBUTING.md) explains the review and packaging process. The Pages build stages a fixed list of documentation and presentation assets; it does not publish a working directory, local profiles, or lab state. GitHub Actions builds the static documentation with repository-scoped permissions. No runtime integration calls company services.
