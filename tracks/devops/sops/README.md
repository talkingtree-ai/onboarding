# Practice operating procedures

These are generic learning templates for your own disposable lab. They are not company runbooks, a control framework, or instructions to operate company systems. No practice report or evidence submission is required. Formal access and team-specific responsibilities belong to a separate onboarding process.

| Procedure | Practice outcome |
| --- | --- |
| [Status and triage](status-and-triage.md) | Find the failing boundary before changing anything |
| [Incident response](incident-response.md) | Restore a synthetic workflow and retain useful evidence |
| [Change and rollback](change-and-rollback.md) | Make a scoped change with a verifiable recovery path |
| [Backup and restore](backup-and-restore.md) | Recover synthetic data into a distinct destination |
| [Secrets and access](secrets-and-access.md) | Reason about least privilege, rotation, and revocation |
| [Patching](patching.md) | Upgrade one layer while preserving recovery options |

For local DNS record changes, the [routing guide](../docs/routing-and-dns.md#practice-a-dns-change-and-rollback) adds a zone-specific change and rollback exercise using the private lab domain.

For local notes, copy the relevant template into an ignored scratch directory. Write UTC timestamps, the selected lab/context, the observation, and the result. Do not collect tokens, cookies, secrets, sensitive URLs, or personal data. A concise reproducible observation is more useful than a large unsanitized log dump.
