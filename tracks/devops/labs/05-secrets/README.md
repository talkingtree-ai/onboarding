# Lab 05 — Local secrets with SOPS and age

Practice encrypting a synthetic Kubernetes Secret, protecting a decryption key, and changing recipients. After installing the tools, the exercise uses local files only. Use a disposable VM or account without existing SOPS configuration or credentials; inherited configuration can add key sources. These commands were tested with SOPS 3.13.3 and age 1.3.2. Use the [official SOPS installation guide](https://getsops.io/docs/installation/) and [age releases](https://github.com/FiloSottile/age/releases), and verify downloaded binaries. Review compatibility when selecting another release.

## 1. Generate a disposable key

Run from this lab directory in Bash. Use a fresh `.local/` directory and do not overwrite an existing key:

```bash
sops --disable-version-check --version
age-keygen --version
umask 077
mkdir -p .local
test ! -e .local/identity.txt
age-keygen -o .local/identity.txt
lab_recipient=$(age-keygen -y .local/identity.txt)
```

`age-keygen` reports a public recipient. The identity file holds the private key and stays ignored. Keep real recovery keys in a separately secured backup: losing the only decryption key loses access to encrypted data. These particular keys are disposable lab material.

## 2. Encrypt and prove a round trip

Create an intentionally fake secret:

```bash
cat > .local/secret.yaml <<'YAML'
apiVersion: v1
kind: Secret
metadata:
  name: synthetic-example
  namespace: onboarding-demo
type: Opaque
stringData:
  training-message: fictional-value-for-learning
YAML

sops --indent 2 encrypt --age "$lab_recipient" \
  --encrypted-regex '^(data|stringData)$' \
  .local/secret.yaml > .local/secret.enc.yaml

SOPS_AGE_KEY_FILE="$PWD/.local/identity.txt" \
  sops --indent 2 decrypt .local/secret.enc.yaml > .local/restored.yaml
cmp .local/secret.yaml .local/restored.yaml
```

Expected: `cmp` exits successfully. SOPS serializes YAML again; `--indent 2` matches this fixture's formatting so the byte comparison works. This is not a promise that arbitrary YAML formatting will survive unchanged. Inspect `.local/secret.enc.yaml`: the value under `stringData` is ciphertext, while the resource name and namespace are readable. SOPS stores recipient metadata and a message authentication code. It does not hide every piece of metadata. Keep plaintext and identities out of Git even if they are synthetic; this builds the right habit. See [SOPS usage](https://getsops.io/docs/usage/) for encryption behavior.

Kubernetes accepts base64-encoded Secret data without SOPS, but base64 is reversible encoding. SOPS protects bytes in storage and transit through Git; authorized software must decrypt them before use. Kubernetes RBAC and encryption at rest are separate controls. [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) explains the cluster-side model.

## 3. Practice changing a recipient

Generate a second disposable key, then re-encrypt the same fake input to that recipient:

```bash
test ! -e .local/identity-next.txt
age-keygen -o .local/identity-next.txt
lab_next_recipient=$(age-keygen -y .local/identity-next.txt)
sops --indent 2 encrypt --age "$lab_next_recipient" \
  --encrypted-regex '^(data|stringData)$' \
  .local/secret.yaml > .local/secret-next.enc.yaml
SOPS_AGE_KEY_FILE="$PWD/.local/identity-next.txt" \
  sops --indent 2 decrypt .local/secret-next.enc.yaml > .local/restored-next.yaml
cmp .local/secret.yaml .local/restored-next.yaml
```

For a clean wrong-key check, temporarily isolate any other SOPS/age key configuration in your disposable VM, then try decrypting `secret-next.enc.yaml` with only `identity.txt`. It should fail. SOPS can also discover environment-provided, system, or SSH-backed identities; merely setting one wrong file does not prove that no other valid identity is available.

This exercise changes an encryption recipient. Real secret rotation also changes the underlying credential at its issuer, distributes it safely, verifies consumers, and revokes the old credential. Re-encrypting the same value alone is not credential rotation. Historical ciphertext can remain decryptable to the old recipient.

## 4. Connect the idea to Flux

Read the [Flux SOPS guide](https://fluxcd.io/flux/guides/mozilla-sops/) and identify the decryption provider and Secret reference on a Flux Kustomization. A separate bootstrap step places the private age identity into the cluster; the private key must never sit beside the ciphertext in Git or an OCI artifact. Access to that cluster key permits decryption.

There is no automatic key import in this exercise. The earlier Flux lab publishes rendered non-secret manifests only. A production secret design also needs key recovery, access review, auditability, and a plan to move to a managed secret store where appropriate. Read the [secrets SOP](../../sops/secrets-and-access.md).

## Cleanup

The following deletes only the disposable files created above. It deliberately destroys the lab's private keys; no real credential belongs here:

```bash
rm -f .local/identity.txt .local/identity-next.txt \
  .local/secret.yaml .local/secret.enc.yaml .local/secret-next.enc.yaml \
  .local/restored.yaml .local/restored-next.yaml
unset lab_recipient lab_next_recipient
```

Deleting files is not a promise of secure erasure on an SSD or snapshotted VM. Use the disposable VM's lifecycle and encrypted host storage for a realistic boundary.
