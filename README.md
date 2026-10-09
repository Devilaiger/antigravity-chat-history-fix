# Antigravity IDE Conversation History Integrity & Recovery

[![Antigravity IDE](https://img.shields.io/badge/Antigravity%20IDE-2.17.x-blue.svg)](https://antigravity.google)
[![SQLite Integrity](https://img.shields.io/badge/SQLite%20Integrity-100%25%20Verified-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/Tests-5%20Passing-success.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A forensic investigation, root-cause analysis, and validated recovery tool for a Google Antigravity IDE conversation-history persistence issue.

---

### Status
- **Investigation:** Complete
- **Root cause:** Identified
- **Local recovery:** Validated
- **Restart persistence:** Validated
- **Production fix:** Not claimed — proposed reconciliation architecture only

---

## 📌 Executive Summary

In Google Antigravity IDE (e.g., version 2.17.x), users experience a failure mode where past chat conversations vanish from the **History** and **Search** interfaces, despite their underlying SQLite `.db` conversation files remaining healthy and intact on disk.

The key architectural issue identified is that the persisted History summary state behaves as an event-derived projection, without a corresponding steady-state reconciliation path from the authoritative conversation database set.

---

## 🔬 Observed Failure

On the affected installation, an audit between the durable store and the UI index revealed:

| Metric | Result | Meaning / Implication |
| :--- | :---: | :--- |
| **Conversation databases** | **58** | Authoritative `.db` files present on disk |
| **Healthy SQLite databases** | **58** | Passed `PRAGMA quick_check = ok` (0% corruption) |
| **Persisted History summaries** | **25** | Total items registered in `trajectorySummaries` |
| **Valid DBs represented in summaries** | **1** | Only 1 valid conversation was visible in History |
| **Missing valid conversations** | **57** | **98.3% of valid conversations were hidden from UI** |
| **Orphan summary entries** | **24** | Index records pointing to non-existent databases |
| **Affected conversation steps** | **329** | Single anchor session (`c99ca0b3`) restored completely |

The discrepancy was reproducible by comparing the authoritative conversation store with the persisted History projection.

---

## 🏗️ Architectural Root Cause

The defect arises because the index is updated solely through in-memory runtime events, without a bidirectional synchronization mechanism against the database directory.

### Failure Path (Event Projection Without Reconciliation)

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

1. **Authoritative Store:** `%USERPROFILE%\.gemini\antigravity-ide\conversations\*.db` contains the ground-truth conversation logs.
2. **Runtime Projection:** `%APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb` (`antigravityUnifiedStateSync.trajectorySummaries`) is updated via frontend `create` events.
3. **Lazy-Hydration Lockout:** Unindexed sessions never render in the History UI. Because they are never selected, `getCascadeTrajectory` is never triggered, and the conversation never hydrates into memory.
4. **Shutdown Snapshot:** During IDE shutdown, `saveAllTopics` overwrites the persistent state with whatever resides in the current in-memory map. Omitted conversations remain omitted indefinitely.

### Proposed Integrity Invariant

Based on the observed failure and recovery process, I propose the following integrity invariant for the History projection:

$$\forall db \in \text{Conversations}_{\text{valid}} \iff \exists ! \, summary \in \text{trajectorySummaries}$$

> *Every valid authoritative conversation database should have a corresponding valid History summary, and every persisted History summary should correspond to an existing authoritative conversation database.*

---

## 🛠️ Recovery & Reconciliation Solution

This repository provides [`src/reconcile_antigravity_history.py`](src/reconcile_antigravity_history.py), a non-destructive, idempotent reconciliation tool:

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

### What This Project Does
- Reads conversation databases without modifying them.
- Reconstructs missing History summaries.
- Removes orphaned summary entries.
- Preserves valid existing summaries.
- Creates an automatic backup before state modification.
- Refuses to operate while Antigravity is running.
- Supports idempotent reconciliation.
- Validates restart persistence.

### What This Project Does Not Do
- Does not modify conversation `.db` files.
- Does not delete conversation history.
- Does not modify Antigravity application binaries.
- Does not claim to be an official Google fix.
- Does not guarantee compatibility with future Antigravity releases.
- Does not claim to repair every possible form of lost conversation data.

---

## 📊 Validation Scorecard

| Test | Expected Result | Measured Result | Status |
| :--- | :--- | :--- | :---: |
| **SQLite integrity check** | All DBs pass `PRAGMA quick_check` | 58/58 DBs OK | **PASS** |
| **58/58 DBs readable** | Read metadata without error | 58/58 readable | **PASS** |
| **Missing-summary reconstruction** | Reconstruct missing entries | 57 restored | **PASS** |
| **Orphan removal** | Prune phantom IDs with no DB | 24 pruned | **PASS** |
| **Damaged-summary reconstruction** | Rebuild malformed metadata | Handled cleanly | **PASS** |
| **Idempotent second run** | Subsequent run executes 0 writes | Clean NO-OP | **PASS** |
| **Clean Antigravity restart** | Normal IDE boot | Passed | **PASS** |
| **Repaired history survives restart** | Retained across `saveAllTopics` | 100% retained | **PASS** |
| **New conversation survives restart** | New sessions persist normally | Passed | **PASS** |
| **Conversation DB modification** | Ground-truth DBs untouched | **NONE** | **PASS** |

Detailed validation protocol and metrics are documented in [`docs/VALIDATION.md`](docs/VALIDATION.md).

---

## 🚀 Quick Usage

### Prerequisites
- Python 3.8+ (standard library only; no external package dependencies required)
- Close Antigravity IDE before running the reconciler.

### 1. Read-Only Diagnostic Check (Safe)
Inspect local conversation files and report current drift without modifying any state:
```bash
python src/reconcile_antigravity_history.py --check
```

### 2. Apply Reconciliation
Automatically backfill missing sessions, prune orphans, and create a pre-mutation backup:
```bash
python src/reconcile_antigravity_history.py --apply
```

### 3. Run Automated Test Suite
Run the included pytest suite to verify parser, reconciliation, and idempotence invariants:
```bash
pytest tests/
```

---

## 📂 Repository Layout

```
antigravity-chat-history-fix/
├── README.md                                          # Project overview and executive summary
├── LICENSE                                            # MIT License
├── SECURITY.md                                        # Safety invariants and data protections
├── CHANGELOG.md                                       # Release notes and history
├── problem.md                                         # Detailed incident problem statement
├── Antigravity_History_Forensic_Postmortem_...pdf     # 21-page deep forensic investigation report
│
├── src/
│   └── reconcile_antigravity_history.py              # Production-grade reconciliation CLI
│
├── tests/
│   ├── conftest.py                                    # Mock fixtures for SQLite stores
│   ├── test_manifest.py                               # DB inspection and manifest generation tests
│   ├── test_reconciliation.py                         # Backfill and orphan pruning tests
│   └── test_idempotence.py                            # Idempotent execution and zero-write tests
│
├── docs/
│   ├── ROOT_CAUSE.md                                  # Architectural analysis of the defect
│   ├── ARCHITECTURE.md                                # Store topologies and synchronization flow
│   ├── VALIDATION.md                                  # Empirical verification scorecard
│   └── LIMITATIONS.md                                 # Operational boundaries and scope
│
├── evidence/
│   ├── RECOVERY_REPORT.md                             # Incident reconciliation report
│   └── AUTHORITATIVE_CONVERSATION_MANIFEST.csv        # Sanitized inventory schema and sample rows
│
└── prompts/                                           # Prompt library for agent workflows
    ├── README.md
    ├── diagnostic.md
    ├── master-recovery.md
    ├── verification.md
    └── emergency-rollback.md
```

> [!NOTE]
> The repository also contains the investigation prompts used during the forensic reconstruction in the [`prompts/`](prompts/) directory.
