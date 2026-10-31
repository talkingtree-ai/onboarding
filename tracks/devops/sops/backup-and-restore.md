# SOP: backup and restore drill

**Trigger:** practice recovery or prepare for a state-changing operation. **Success:** recover synthetic data into a separate destination and verify it is usable.

## Define recovery before choosing a command

- **RPO:** the acceptable amount of lost data, expressed as a time window.
- **RTO:** the target time to restore useful service.
- **Scope:** configuration, application data, keys, and infrastructure state may require different recovery methods.

Use invented lab targets, such as “lose at most the last manual edit” and “restore this two-record fixture.” These are practice targets, not company objectives. A backup file's existence proves neither freshness nor restorability.

## Procedure

1. Inventory the authoritative data, versions, storage locations, encryption keys, and cross-store references. Decide how to obtain a consistent backup: quiesce toy writes or use the database's supported consistency mechanism. Copying a live database directory blindly can create an unusable backup.
2. Create synthetic records with known count, IDs, and content hashes. Record the backup start/end, tool version, format, size, and selected consistency method. Avoid credential-bearing command lines and logs.
3. Use the relevant supported method. A document database export, vector snapshot, object copy, cache persistence file, and cluster datastore backup protect different data. Do not substitute one for all the others.
4. Restrict backup access. Keep any decryption material separate and recoverable. A second directory on one disk is useful for a drill but shares the disk's failure domain. Production recovery requires independently designed retention and failure isolation.
5. Restore into a distinct lab instance, volume, database, or collection. Keep the original untouched. Confirm tool/server compatibility before restoring.
6. Verify record count, selected hashes, index definitions, object references, permissions, and an application read. For synthetic vectors, confirm collection dimension/metric and an expected query. Record elapsed recovery time and any manual steps.
7. Retain or remove the synthetic restore destination deliberately. Do not run blanket volume pruning. Note failures and improve the procedure before trusting the next backup.

## Know the boundary

| Component | Supported concept | Additional concern |
| --- | --- | --- |
| MongoDB | [mongodump](https://www.mongodb.com/docs/database-tools/mongodump/) and matching restore tooling | Consistency under concurrent writes and server/tool compatibility |
| Qdrant | [Snapshots](https://qdrant.tech/documentation/operations/snapshots/) | Collection versus cluster scope; version compatibility |
| Valkey | [RDB/AOF persistence](https://valkey.io/topics/persistence/) | Is loss acceptable, or does the store carry durable work? |
| Object store | Store-supported object/metadata copy or snapshot | Versions, permissions, cross-store consistency, and delete behavior |
| K3s control plane | [Datastore-specific backup](https://docs.k3s.io/datastore/backup-restore) | Preserve required server token securely; this does not back up application volumes |
| Git/Terraform | Versioned configuration / protected state | Neither restores application records or external secret values |

```text
Synthetic data scope / authoritative sources:
Practice RPO / RTO:
Backup time / consistency method / versions:
Backup identifier / size / checksum:
Key recovery plan (no key values):
Distinct restore destination:
Verification: counts / hashes / indexes / application reads
Elapsed recovery / gaps:
Cleanup performed:
```
