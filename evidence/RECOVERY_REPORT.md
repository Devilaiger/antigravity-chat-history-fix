# Incident Recovery Report: Antigravity Conversation Index Parity

## 1. Incident Overview
- **Product:** Google Antigravity IDE (v2.17.x)
- **Component:** Conversation History & Search (`antigravityUnifiedStateSync.trajectorySummaries`)
- **Classification:** Index Drift / Incomplete Event-Derived Projection
- **Authoritative Data Loss:** **0%** (All 58 SQLite databases intact and healthy)

---

## 2. Quantitative Store Comparison

Prior to running reconciliation, an audit comparing the local conversation database store with `state.vscdb` yielded:

| Metric | Measured Value | Implication |
| :--- | :---: | :--- |
| **Total `.db` Files on Disk** | **58** | Authoritative conversation files in storage |
| **Pass `PRAGMA quick_check`** | **58 (100%)** | Zero database file corruption |
| **Persisted Summary Entries** | **25** | Total entries in `trajectorySummaries` |
| **Matching Valid Sessions** | **1** | Only 1 valid file represented in History UI |
| **Missing Sessions in UI** | **57 (98.3%)** | Conversations durable on disk but hidden from user |
| **Phantom / Orphan Summary Keys** | **24** | Index entries with no backing `.db` on disk |
| **Affected Steps (Anchor `c99`)** | **329** | Multi-turn active session restored completely |

---

## 3. Reconciliation Actions Performed
1. Pre-mutation snapshot archived to `state.vscdb.backup_<timestamp>`.
2. Extracted canonical cascade IDs, titles, and timestamps from all 58 conversation databases.
3. Constructed consolidated summary payload mapping all 58 valid cascade IDs.
4. Pruned 24 orphaned keys.
5. Committed state atomically to `ItemTable` in `state.vscdb`.
6. Verified subsequent run performed 0 writes (idempotent NO-OP).
7. Verified full retention through graceful IDE shutdown and cold relaunch.
