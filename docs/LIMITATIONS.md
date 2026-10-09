# Project Scope & Known Limitations

## 1. What This Project Does
- **Reads conversation databases non-destructively:** Strictly opens `.db` files in read-only mode to extract metadata and verify SQLite integrity.
- **Reconstructs missing History summaries:** Backfills healthy conversations that were omitted from `trajectorySummaries`.
- **Removes orphaned summary entries:** Prunes phantom records in `state.vscdb` that point to non-existent conversation files.
- **Preserves valid existing summaries:** Retains user metadata and timestamps for already-indexed conversations.
- **Automated rollback protection:** Automatically creates an immutable timestamped backup of `state.vscdb` before any modification.
- **Enforces process mutual exclusion:** Refuses execution while Antigravity is running to avoid SQLite lock collisions.
- **Guarantees idempotence:** Consecutive executions on a synchronized system perform 0 writes.

---

## 2. What This Project Does Not Do
- **Does not modify conversation `.db` files:** The underlying conversation store is treated as read-only.
- **Does not delete conversation history:** Only phantom summary index references with missing backing files are pruned from the UI index.
- **Does not modify Antigravity application binaries:** It leaves VS Code core files, extension host bundles, and binaries completely untampered.
- **Does not claim to be an official upstream Google patch:** This is an independent, empirically validated local recovery fix and an architectural proposal submitted for engineering review.
- **Does not guarantee compatibility with unreleased Antigravity versions:** Future internal schema changes to `antigravityUnifiedStateSync.trajectorySummaries` may require updated serializers.
- **Does not recover physically erased files:** If a conversation `.db` file was deleted from disk, wiped, or truncated, this tool cannot recover unrecorded turns.
