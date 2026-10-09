# Architecture Specification: Conversation History Persistence

This document details the internal data flow, state serialization models, and reconciliation architecture of Google Antigravity IDE.

---

## 1. Storage Boundaries & Lifecycles

```
AUTHORITATIVE STORE
conversations/*.db
        │
        │ missing reconciliation
        ▼
┌───────────────────┐
│trajectorySummaries│
│  event projection │
└─────────┬─────────┘
          │ shutdown snapshot
          ▼
     state.vscdb
          │
          ▼
   History / Search
```

### Authoritative Conversation Store
- **Path:** `%USERPROFILE%\.gemini\antigravity-ide\conversations\{cascade_id}.db`
- **Schema:**
  - `trajectory_meta`: Contains `trajectory_id`, `cascade_id`, `trajectory_type`, `source`.
  - `steps`: Sequential log of user prompts, assistant turns, tool calls, and execution payloads.
  - `trajectory_metadata_blob`: Additional workspace and configuration blobs.
- **Integrity Guarantee:** SQLite format 3, WAL/standard journal modes. Verified using `PRAGMA quick_check`.

### History Summary Projection
- **Path:** `%APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb`
- **Storage Structure:** `ItemTable (key TEXT PRIMARY KEY, value BLOB/TEXT)`
- **Target Key:** `antigravityUnifiedStateSync.trajectorySummaries`
- **Role:** High-speed in-memory cache used by the VS Code extension host to display past sessions in the sidebar without opening dozens of SQLite files on startup.

---

## 2. The Reconciliation Architecture

To solve index drift without modifying core IDE binaries, this project implements an **External Reconciliation Boundary**:

```
conversation DBs
        │
        ▼
  reconciliation
    ┌──┴──┐
    ▼     ▼
 missing orphan
   add   remove
    └──┬──┘
       ▼
trajectorySummaries
       │
       ▼
 History / Search
```

### Safety Rules:
1. **Immutable Databases:** Conversation databases are opened with SQLite URI `?mode=ro`. The reconciler strictly performs zero writes to `.db` files.
2. **Process Mutual Exclusion:** The reconciler verifies that `Antigravity.exe` is not running before mutating `state.vscdb`.
3. **Atomic Backups:** An immutable copy (`state.vscdb.backup_<timestamp>`) is generated prior to committing changes.
4. **Strict Idempotence:** If no drift exists between disk and index, exactly zero writes are performed.
