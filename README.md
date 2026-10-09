# Antigravity IDE Conversation History Integrity

### Forensic analysis, root-cause reconstruction, and validated recovery of missing History/Search entries.

[![Antigravity IDE](https://img.shields.io/badge/Antigravity%20IDE-2.17.x-blue.svg)](https://antigravity.google)
[![SQLite Integrity](https://img.shields.io/badge/SQLite%20Integrity-100%25%20Verified-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/Tests-5%20Passing-success.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A comprehensive forensic investigation, root-cause analysis, and validated recovery tool for Google Antigravity IDE conversation-history persistence.

---

### Project Status
| Stage | Status | Details |
| :--- | :---: | :--- |
| **Forensic Investigation** | Complete | Root cause identified and empirically proven |
| **Local Recovery Fix** | Tested & Working | 100% restored (57/57 missing sessions restored, 0 DB data loss) |
| **Restart Durability** | Passed & Verified | Reconciled state survives cold restarts & `saveAllTopics` |
| **Fault Injection** | Passed & Verified | Simulated drift converged back to 100% store parity |
| **Upstream IDE Engine Patch** | Proposed Architecture | Submitted to Google engineering for native in-engine adoption |

---

## 📌 Executive Summary

In Google Antigravity IDE (e.g., version 2.17.x), users frequently encounter an issue where past chat conversations vanish from the **History** and **Search** interfaces, despite their underlying SQLite `.db` conversation files remaining healthy and intact on disk.

### The Architectural Differentiator
This project is not simply another index wipe or restore script. It traces the native runtime architecture (`CascadeManager`, `trajectoryFetcherImpl`, `saveAllTopics`) to explain **why** the projection permanently diverges:

> *The key architectural issue identified is that the persisted History summary state behaves as an event-derived projection, without a corresponding steady-state reconciliation path from the authoritative conversation database set.*

---

## 🔬 Observed Failure (Quantitative Evidence)

On the affected installation, an audit between the durable store and the UI index revealed:

| Metric | Result | Meaning / Implication |
| :--- | :---: | :--- |
| **Actual Valid `.db` Conversations** | **58** | Authoritative conversation databases on disk |
| **Persisted Summary Entries** | **25** | Total items registered in `trajectorySummaries` |
| **Matching Valid IDs** | **1** | Only 1 valid conversation was visible in History |
| **Invisible Conversations** | **57** | **98.3% of valid conversations were hidden from UI** |
| **Orphan IDs** | **24** | Index records pointing to non-existent databases |
| **Database Corruption** | **0** | SQLite `PRAGMA quick_check = ok` across all 58 |
| **Affected Conversation Steps** | **329** | Multi-turn anchor session (`c99ca0b3`) restored completely |

The discrepancy was reproducible by comparing the authoritative conversation store with the persisted History projection.

---

## 🏗️ Architectural Root Cause

The defect arises because the index is updated solely through runtime frontend events, without a bidirectional synchronization mechanism against the database directory.

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

1. **Authoritative Store:** `%USERPROFILE%\.gemini\antigravity-ide\conversations\*.db` contains ground-truth turns, prompts, and tool invocations.
2. **Runtime Projection:** `%APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb` (`antigravityUnifiedStateSync.trajectorySummaries`) is updated only via in-session `create` events.
3. **Lazy-Hydration Catch-22:** Unindexed sessions never render in the History UI. Because they are never clicked, `getCascadeTrajectory` is never called, and the session never hydrates into `CascadeManager`.
4. **Shutdown Snapshot Overwrite:** During graceful IDE shutdown, `saveAllTopics` overwrites the persistent state with whatever resides in the current in-memory map. Omitted conversations remain omitted indefinitely.

### Proposed Integrity Invariant

Based on the observed failure and recovery process, I propose the following integrity invariant for the History projection:

$$\forall db \in \text{Conversations}_{\text{valid}} \iff \exists ! \, summary \in \text{trajectorySummaries}$$

> *Every valid authoritative conversation database should have a corresponding valid History summary, and every persisted History summary should correspond to an existing authoritative conversation database.*

---

## 🛠️ Recovery & Reconciliation Implementation

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
- Reconstructs missing History summaries directly from `.db` metadata.
- Removes orphaned summary entries pointing to non-existent files.
- Preserves valid existing summaries.
- Creates an automatic timestamped backup of `state.vscdb` before any modification.
- Refuses to operate while Antigravity is running (process mutual exclusion guard).
- Supports idempotent reconciliation (consecutive runs execute 0 writes).
- Validates restart persistence across cold IDE boots.

### What This Project Does Not Do
- Does not modify conversation `.db` files.
- Does not delete conversation history.
- Does not modify Antigravity application binaries (operates externally via safe SQLite state reconciliation).
- Does not claim to be an official upstream Google patch (it is a validated local recovery tool and proposed in-engine architectural fix).
- Does not guarantee compatibility with future unreleased internal schema changes.
- Does not claim to repair physically deleted or truncated database files.

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
- Ensure Antigravity IDE is closed before applying reconciliation.

### 1. Read-Only Diagnostic Check (Safe)
Inspect local conversation files and report current drift without modifying any state:
```bash
python src/reconcile_antigravity_history.py --check
```

### 2. Apply Reconciliation
Backfill missing sessions, prune orphans, and create an automated pre-mutation backup:
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
    ├── README.md                                      # Prompt library index
    ├── opencode-fix-prompt.md                         # Tailored prompt for OpenCode
    ├── kilo-code-cli-fix-prompt.md                    # Tailored prompt for Kilo Code CLI
    ├── codex-fix-prompt.md                            # Tailored prompt for OpenAI Codex
    ├── master-recovery.md                             # Universal / Claude Code recovery prompt
    ├── diagnostic.md                                  # Safe read-only audit prompt
    ├── verification.md                                # Verification and durability test prompt
    └── emergency-rollback.md                          # Backup restoration prompt
```

> [!NOTE]
> Tested prompts for specific coding agents (**OpenCode**, **Kilo Code CLI**, **OpenAI Codex**, and **Claude Code / Antigravity**) are preserved in the [`prompts/`](prompts/) directory.
