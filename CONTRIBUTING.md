# Maintaining and sharing the material

Keep examples independently runnable, original, and free of private implementation details. Use public vendor documentation for explanations and verify commands against a named version. A technology name can be relevant without revealing an organization's deployment details. Do not add real hosts, account IDs, internal repository links, employee contacts, allowlists, customer information, or credentials.

## Before changing a lab

Explain its learning objective, prerequisites, expected result, failure symptoms, and cleanup. Prefer local resources with fixed lab names and explicit target contexts. Avoid paid APIs, cloud free-tier assumptions, public listeners, account-dependent bootstrapping, and tools that silently mutate a learner's default kubeconfig. Keep optional hosted exercises separate from the core path.

Run `python3 scripts/verify.py`. Perform the relevant runtime checks on your own disposable environment after changing runtime files. Update [VALIDATION.md](VALIDATION.md) with what actually ran, tool versions, and what remains untested. A static YAML parse is not a Kubernetes or Flux integration test.

Review updates to upstream image tags, tool releases, security support, and account terms before distributing a new revision. Tagged images are easier to inspect than `latest`, but tags can move; a more advanced exercise can pin a verified multi-architecture digest. Third-party tools retain their own licenses. This educational repository is published through GitHub and GitHub Pages; it contains no company application source or private assets. An open-source license for the original material has not been selected.

## Before sharing a copy

Review the complete file list, diff, and any Git history for secrets and private information. The local static check catches a few common patterns; it is not a complete secret scanner or a substitute for review. Keep learner-generated files untracked. Do not copy a whole workspace or another repository's history into this one.

Once a reviewed revision is committed, an archive includes only its tracked contents:

```bash
git status --short
git ls-files
git log --oneline --all
git archive --format=zip --output=../onboarding-materials.zip HEAD
```

Run that command only when you intend to make a shareable archive. It creates a local file and does not upload it. Review the archive's contents before distributing it. Omit `.git/` and all local lab state. Public updates must preserve the same separation from private company material; see the [public-release review](PUBLIC-RELEASE.md).

## Adding another track

Replace a placeholder's README with its own audience, optional learning path, public references, and independent examples. Shared tooling can live in `examples/` or `scripts/`. Maintain relative links so a downloaded archive works without any hosted repository.

Formal company onboarding, access approval, and company policies belong in the appropriate authorized internal process. This material should remain useful without them.
