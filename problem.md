# Antigravity Conversations Disappearing from History: Problem Specification

> [!WARNING]
> **Issue Summary:** Conversations vanish from the Google Antigravity History & Search UI even though their underlying `.db` conversation files remain completely intact, valid, and healthy on disk.

---

## 1. Executive Problem Statement

In Google Antigravity IDE (e.g. version 2.17.x), users experience a severe and recurring issue where past chat sessions suddenly disappear from the **History** and **Search** views. 

Forensic analysis proves that:
1. **The conversations are NOT deleted.** All conversation `.db` files remain present on disk in `%USERPROFILE%\.gemini\antigravity-ide\conversations\`.
2. **The databases are NOT corrupted.** Every missing conversation passes SQLite integrity checks (`PRAGMA quick_check = ok`) and contains all prompts, assistant responses, and trajectory steps.
3. **The History UI relies on an ephemeral, event-derived projection** (`antigravityUnifiedStateSync.trajectorySummaries`) persisted in `%APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb`.
4. **There is NO startup backfill or reconciliation** between the conversation store (`*.db`) and the summary state. 

Because a conversation missing from History is never rendered in the UI, the user cannot select it. Because it is never clicked/selected, its ID is never requested through Antigravity's lazy loader (`getCascadeTrajectory`), meaning it never enters the in-memory `CascadeManager` registry. The conversation becomes **durable on disk, but permanently invisible in the IDE**.

---

## 2. Forensic Discrepancy Evidence

During forensic investigation of an affected system, the durable store and the index projection had drastically diverged:

| Metric | Measured Value | Meaning / Implication |
| :--- | :---: | :--- |
| **Actual Valid `.db` Conversations** | **58** | Authoritative conversation databases on disk |
| **Persisted Summary Entries** | **25** | Total items in `trajectorySummaries` |
| **Matching Valid IDs** | **1** | Only 1 valid `.db` was indexed and visible |
| **Invisible / Missing Valid Conversations** | **57** | **98.3% of valid conversations were hidden!** |
| **Orphan / Phantom Summary IDs** | **24** | IDs in History index pointing to nonexistent files |
| **SQLite Quick Check Result** | **100% OK** | Zero file corruption across all 58 databases |

---

## 3. Architectural Root Cause

The core defect is a **unidirectional, event-only architectural mismatch**:

```
           +-------------------------------------------------------+
           |       Authoritative Store (Durable Disk Layer)        |
           |     %USERPROFILE%\.gemini\antigravity-ide\conversations\     |
           |                     58 Healthy *.db files              |
           +-------------------------------------------------------+
                                      |
                     [ X ] NO STARTUP RECONCILIATION
                           NO DISK-TO-INDEX BACKFILL
                                      |
                                      v
           +-------------------------------------------------------+
           |    Summary Projection (Ephemeral StateSync Layer)     |
           |          antigravityUnifiedStateSync.trajectorySummaries       |
           |      Updated ONLY via runtime frontend create events   |
           +-------------------------------------------------------+
                                      |
                                      v
           +-------------------------------------------------------+
           |                   Antigravity History UI              |
           |               Only displays what is in summary        |
           +-------------------------------------------------------+
```

### Why Restarting Does Not Fix It
1. **Runtime Mutation:** `trajectorySummaries` is only updated when a `create` event is pushed by the frontend during an active chat session.
2. **Shutdown Overwrite:** At application shutdown, Antigravity serializes the entire in-memory summary map and overwrites `state.vscdb` (`saveAllTopics`).
3. **Circular Loss:** If a conversation's `create` event was missed (or occurred in a different context/window), it never enters the summary map. At shutdown, the incomplete map is saved back to disk. When Antigravity restarts, it seeds itself from the same incomplete map, leaving the valid conversations hidden indefinitely.

---

## 4. Disproven Hypotheses

Forensic investigation ruled out several common assumptions:

- ❌ **NOT a 25-conversation eviction cap:** The hard cleanup limit in the codebase is 100 entries (based on `lastModifiedTime`). The 25 entries found were simply whatever happened to be trapped in the snapshot.
- ❌ **NOT SQLite database corruption:** Every database passed `PRAGMA integrity_check` and `PRAGMA quick_check`.
- ❌ **NOT `.gemini\antigravity-cli` collision:** The CLI and IDE maintain distinct process profiles and data roots.
- ❌ **NOT missing `.pb` files:** Modern Antigravity versions use SQLite `.db` as the authoritative format, not legacy protobuf blobs.
- ❌ **NOT Workspace UI filtering alone:** While the UI filters by workspace URI, 57 conversations were missing from the index entirely before filtering even occurred.

---

## 5. The Solution Invariant

To permanently resolve this issue, the system must enforce a strict two-way consistency invariant:

$$\text{Every valid } *.db \iff \text{Exactly one valid entry in } trajectorySummaries$$

1. **Reconstruct:** Extract authoritative metadata (cascade ID, title, timestamps, workspace URI, step counts) directly from all valid `.db` files and populate `antigravityUnifiedStateSync.trajectorySummaries`.
2. **Purge:** Remove all phantom/orphan IDs that do not map to an existing `.db` file.
3. **Automate (Self-Healing):** Run an automated, idempotent reconciliation layer before IDE startup (or on system logon / hourly) that detects drift and synchronizes the store safely without touching or corrupting database files.

---

## 6. Technical File References

| Component | Path / Location |
| :--- | :--- |
| **Conversation Databases** | `%USERPROFILE%\.gemini\antigravity-ide\conversations\*.db` |
| **Trajectory Brain Directories** | `%USERPROFILE%\.gemini\antigravity-ide\brain\{cascadeId}\` |
| **Global Storage Database** | `%APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb` |
| **Indexed SQLite Table** | `ItemTable (key TEXT, value BLOB)` |
| **State Sync Key** | `antigravityUnifiedStateSync.trajectorySummaries` |
| **Secondary Index Key** | `chat.ChatSessionStore.index` |
