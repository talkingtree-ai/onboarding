#!/usr/bin/env bash
set -euo pipefail

lab_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$lab_dir"
command -v openssl >/dev/null || { printf '%s\n' 'Install OpenSSL before this optional exercise.' >&2; exit 1; }

if [[ -L .local || -L .local/certs ]]; then
  printf '%s\n' 'Refusing to write through a .local or certs symlink.' >&2
  exit 1
fi
if [[ -e .local/certs/local.key || -e .local/certs/local.crt ]]; then
  printf '%s\n' 'Lab key/certificate already exists. Inspect it; remove this pair deliberately before regenerating.' >&2
  exit 1
fi

umask 077
mkdir -p -- .local/certs
chmod 0700 .local
chmod 0755 .local/certs
openssl req -x509 -newkey rsa:2048 -sha256 -nodes -days 7 \
  -config tls/openssl.cnf \
  -keyout .local/certs/local.key -out .local/certs/local.crt 2>.local/cert-generation.log
# The host's owner-only .local parent protects this disposable key. The mounted
# child needs to be readable by the isolated proxy's UID 10001; no root required.
chmod 0644 .local/certs/local.key .local/certs/local.crt
printf '%s\n' 'Created a seven-day local certificate in .local/certs; no trust stores changed.'
