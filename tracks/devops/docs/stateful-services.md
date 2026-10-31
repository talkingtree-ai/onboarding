# Optional stateful service exercises

The core labs keep the runnable stack small. This extension teaches the data roles relevant to an application platform without paid AI APIs, customer documents, or cloud accounts. You can do the design exercise entirely on paper; running extra databases is optional and requires your own disposable local setup.

## Design a synthetic notebook service

Use two fake notes: `blue bicycle` and `green kettle`. Assign random local IDs. The following table is an exercise design, not an implementation supplied by the core labs or a product data model.

| Service | Synthetic contents | What can fail independently? | Recovery question |
| --- | --- | --- | --- |
| MongoDB | Note ID, title, object key, revision | Authentication, writes, indexes, incompatible data shape | Can you restore records and index definitions? |
| S3-compatible storage | Plain text note bytes | Missing key, permissions, expiry, metadata/bytes disagreement | Are objects and referenced versions recoverable together? |
| Qdrant | Handwritten fixed-length vectors with note IDs | Wrong dimension, stale payload, missing collection | Can you rebuild the index from original inputs and the same transformation? |
| Valkey | Short-lived cached titles | Expiry, eviction, connection loss | Is it truly a cache, or does it carry durable work? |

Use vectors such as `[1, 0, 0]` and `[0, 1, 0]`; no embedding model or API key is needed. For an actual Qdrant experiment, define the collection dimension and distance metric explicitly and use the current [Qdrant documentation](https://qdrant.tech/documentation/). A synthetic nearest-neighbor result demonstrates index mechanics, not language understanding.

## Optional local implementation plan

If you want to extend the examples yourself:

1. Start one service at a time from its official container instructions. Choose a supported pinned version, verify architecture support and license, set storage limits, and keep ports on loopback or an isolated container network.
2. Give the lab a separate project name and named volumes. Use disposable credentials in ignored local files. Do not mount your home directory or Docker socket into application containers. Local services without authentication must remain unreachable from other machines.
3. Insert the two synthetic notes, retrieve by ID, and compare count, content, and metadata with the expected values. Add a bounded health check; a successful TCP connection is insufficient.
4. Write a tiny client or use official tools to perform the role in the table. Persist only what the chosen exercise needs. Record exactly which data is authoritative and which can be rebuilt.
5. Stop one service. Predict whether reads, writes, search, or cached reads fail. Observe the result, then recover only that service. Never mask missing storage with a successful placeholder response.
6. Use the [backup and restore SOP](../sops/backup-and-restore.md) to restore into a distinct destination. Keep the original intact until record counts, hashes, and application reads are verified.
7. Stop the lab when done. Deleting volumes is a separate deliberate decision after you no longer need the data or restore exercise.

Image downloads and local disk/RAM use are real even without service charges. Choose a single-service exercise on a smaller machine. No AWS endpoint, personal billing account, hosted vector service, or document-processing API is required.

## Questions that make the exercise useful

- If metadata commits but the object upload fails, how does the application find and repair the incomplete record?
- If a note changes, how do you prevent an old search result from presenting the wrong revision?
- If a retry repeats a write, does it create duplicates? What makes an operation idempotent?
- If a cache disappears, can you safely reconstruct every value? What differs for a work queue?
- If a signed object link leaks, how long does access persist? Does the URL itself contain sensitive authority?
- Can you delete a note from every derived store and later demonstrate the deletion using synthetic IDs?

Relevant official reading: [MongoDB database tools](https://www.mongodb.com/docs/database-tools/mongodump/), [Qdrant snapshots](https://qdrant.tech/documentation/operations/snapshots/), and [Valkey persistence](https://valkey.io/topics/persistence/). “S3-compatible” is a protocol goal; confirm behavior in the selected object store's documentation before treating it as equivalent to a managed service.
