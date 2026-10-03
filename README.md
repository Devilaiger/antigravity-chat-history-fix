# 🛰️ Google Antigravity Conversation History Disappearance: Root Cause & Permanent Fix

[![Antigravity](https://img.shields.io/badge/Antigravity%20IDE-2.17.x-blue.svg)](https://antigravity.google)
[![Integrity](https://img.shields.io/badge/SQLite%20Integrity-100%25%20Verified-brightgreen.svg)]()
[![Status](https://img.shields.io/badge/Fix%20Status-Tested%20%26%20Durable-success.svg)]()
[![Safety](https://img.shields.io/badge/Data%20Loss-Zero%20(DBs%20Preserved)-green.svg)]()

> A comprehensive forensic postmortem, root cause analysis, and production-tested recovery suite for the bug where **Google Antigravity IDE past conversations disappear from History and Search**, despite their underlying SQLite `.db` conversation files remaining intact and healthy on disk.

---

## 📌 Executive Summary

Many Antigravity IDE users experience a baffling issue: **past chats and cascades vanish from the History and Search UI**. Users often fear their conversations have been lost or deleted.

### What Actually Happened?
1. **Your conversations are NOT lost.** Antigravity stores conversation history as SQLite databases in `%USERPROFILE%\.gemini\antigravity-ide\conversations\*.db`. Every database remains on disk with all turns, prompts, and code intact.
2. **The History UI is an un-reconciled projection.** The sidebar and search UI read from a separate state table (`antigravityUnifiedStateSync.trajectorySummaries`) in `%APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb`.
3. **No startup backfill exists.** Antigravity updates this summary map only via incremental runtime frontend events. There is no background backfill between the `.db` files on disk and the index.
4. **Shutdown overwrite cycle.** At application shutdown, Antigravity serializes whatever is currently in memory and overwrites the persisted state. Missed events cause valid conversations to be permanently excluded from the index across restarts.

---

## 🔬 Forensic Evidence (From Live Affected Systems)

A forensic deep-dive into an affected Antigravity installation revealed extreme divergence:

| Metric | Measured Value | Meaning / Implication |
| :--- | :---: | :--- |
| **Actual Valid `.db` Conversations on Disk** | **58** | Authoritative SQLite databases with 100% integrity |
| **Persisted Summary Entries in UI Index** | **25** | Total items in `trajectorySummaries` |
| **Matching Valid IDs** | **1** | Only 1 valid conversation was visible in History |
| **Invisible / Missing Valid Conversations** | **57** | **98.3% of chats were hidden from the user!** |
| **Phantom / Orphan Summary IDs** | **24** | Index entries pointing to nonexistent files |
| **Database File Corruption** | **0** | SQLite `PRAGMA quick_check` returned `ok` across all 58 |

---

## 🏗️ Architecture: Before vs. After

### ❌ Before: Event-Only Consistency (Broken Projection)

```
       Durable Disk Store (*.db)
                  │
        [ X ] NO RECONCILIATION
              NO DISK BACKFILL
                  │
                  ▼
       Runtime Frontend Events ────► In-Memory Summary Map
                                              │
                                       Shutdown Snapshot (saveAllTopics)
                                              │
                                              ▼
                                    state.vscdb (Incomplete)
                                              │
                                              ▼
                                         History UI
```

### ✅ After: Explicit Integrity & Self-Healing Boundary

```
       Durable Disk Store (*.db)
                  │
                  ▼
       Reconciliation Layer (Self-Healing Boundary)
                  │
        ┌─────────┴─────────┐
        ▼                   ▼
   Missing Summaries     Orphan Summaries
      Reconstructed          Pruned
        │                   │
        └─────────┬─────────┘
                  ▼
       state.vscdb (100% Parity with Disk Store)
                  │
                  ▼
             History UI (All Chats Visible & Searchable)
```

---

## 🚀 Quick Self-Diagnostic (PowerShell)

Check if your installation is suffering from index drift:

```powershell
# 1. Count actual conversation databases on disk
$dbs = (Get-ChildItem "$HOME\.gemini\antigravity-ide\conversations\*.db").Count
Write-Host "Real conversations on disk: $dbs"

# 2. Check if Antigravity process is active
Get-Process Antigravity -ErrorAction SilentlyContinue | Select-Object Id, ProcessName
```

If you have dozens of `.db` files but only see a handful in your Antigravity History sidebar, **you are affected by this issue.**

---

## 📋 Copyable Prompts for AI Coding Agents

You can resolve this issue permanently using any AI coding assistant (Antigravity itself, Claude Code, Codex, OpenCode, or Cursor). 

> 💡 **How to use:** Click the **Copy** button in the top-right corner of any code block below, paste it into your AI agent, and let it run.

<details open>
<summary><b>🛠️ Prompt 1: Master Recovery & Permanent Prevention Fix (Click to Expand / Collapse)</b></summary>

> 💡 **Quick Copy:** Click the **Copy** button on the top-right of the code block below:

```markdown
You are performing the FINAL RECOVERY + PERMANENT PREVENTION FIX for the Google Antigravity IDE conversation History/indexing bug.

This is NOT a request for another forensic report.

The objective is to:
1. Recover ALL currently valid conversations into Antigravity History.
2. Remove all orphan/phantom History entries.
3. Make History automatically reconcile itself with the real conversation store.
4. Ensure missing frontend summary events can NEVER permanently hide an otherwise valid conversation during normal operation.
5. Verify the fix survives an Antigravity restart.
6. Verify newly created conversations also survive a restart.
7. Preserve a complete rollback path.

======================================================================
                         ABSOLUTE RULES
======================================================================

DO NOT:
- delete any conversation .db file
- delete the brain directories
- clear Antigravity state
- reset Antigravity
- reinstall Antigravity
- factory-reset anything
- blindly edit protobuf bytes
- invent conversation metadata
- fabricate titles or timestamps
- assume a 25-conversation limit
- assume filesystem mtime determines History
- revive the old startup-bulk-hydration theory
- treat state.vscdb as the authoritative conversation store
- overwrite files before creating backups
- modify anything until the current backup is verified
- claim success until the restart tests pass
- make a one-time state.vscdb edit and call it a permanent fix

Do not make destructive changes.
If any step is ambiguous, STOP and investigate the existing implementation before modifying anything.

======================================================================
                      CURRENT KNOWN STATE
======================================================================

Antigravity version: 2.17.x
Antigravity is currently CLOSED.

The conversation store is:
%USERPROFILE%\.gemini\antigravity-ide\conversations\

Global application state is:
%APPDATA%\Antigravity IDE\User\globalStorage\

First:
1. Locate any existing backups.
2. Verify that they exist.
3. Verify the number of conversation databases in the backup.
4. Verify the backup contains the relevant global/profile state.
5. Verify the backup is readable.
6. Record its location.
7. Treat the backup as the immutable rollback source.

Do not modify the backup.

======================================================================
                     ESTABLISHED ARCHITECTURE
======================================================================

A. Conversation store:
   Antigravity stores current conversation databases under:
   %USERPROFILE%\.gemini\antigravity-ide\conversations\
   The .db filename corresponds to the cascade ID.
   The databases pass SQLite integrity checking.
   The conversation store is the authoritative source for the existence of current local conversations.

B. Trajectory store registry:
   The trajectory store enumerates conversations\*.db and registers their IDs internally.
   This does NOT mean those conversations are automatically loaded into CascadeManager.

C. CascadeManager:
   There is NO startup bulk hydration of CascadeManager.
   The proven load path is:
   getCascadeTrajectory -> trajectoryFetcherImpl.GetCascadeTrajectory -> CascadeManager.GetTrajectory -> ensureTrajectoryLoaded -> CascadeManager.LoadTrajectory -> Manager.LoadUnsafe -> processLoadedTrajectory -> updateStateForLoadedTrajectory
   CascadeManager is in-memory. Every LS restart starts with a fresh registry.
   Therefore: .db exists != CascadeManager contains it.
   A conversation becomes loaded only when its cascade ID is requested.

D. History summary state:
   The relevant persisted state is:
   antigravityUnifiedStateSync.trajectorySummaries
   This is NOT an authoritative enumeration of all conversation databases.
   It is maintained through frontend summary events (create, delete, updateAnnotations, updateOptimisticSummary).
   create is the operation capable of introducing a new cascade ID.
   There is no complete enumeration/backfill from conversations\*.db into trajectorySummaries.
   This is the core architectural defect.

E. Persistence:
   The in-memory summary map is updated incrementally.
   At application shutdown, the complete current summary topic is serialized and persisted.
   The persisted topic therefore reflects the event-derived in-memory map.
   It does NOT perform a read/merge/reconciliation against the conversation store before writing.

F. Cleanup:
   The cleanup limit is 100 (NOT 25).
   The cleanup uses the summary's own lastModifiedTime.
   The observed 25-entry state is NOT a 25-item History limit. Do not enforce any 25-item limit.

G. UI filtering:
   The History selector has workspace/metadata filtering:
   - lastUserInputTime
   - trajectoryMetadata.parentConversationId
   - workspaces[].workspaceFolderAbsoluteUri
   This selector is read-only. It does NOT explain missing persisted summaries.

======================================================================
                      KNOWN AFFECTED STATE
======================================================================

Target missing conversation anchor:
cascade ID: c99ca0b3-a658-48ae-9dba-33eed0571a99
- Its .db exists and is a valid SQLite database (passes quick_check).
- Contains steps, prompts, actions, and associated brain data.
- Missing from normal History/Search.

Comparison visible conversation:
cascade ID: 686e30bc-6e67-4f84-b395-5b901354f926
Both databases are structurally valid. The difference is whether the conversation has a persisted summary entry in trajectorySummaries.

======================================================================
                          PHASE 0
                    BACKUP VERIFICATION
======================================================================

Before modifying anything:
1. Locate or create a full backup of:
   - %USERPROFILE%\.gemini\antigravity-ide\conversations\
   - %APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb
2. Verify it contains all conversation databases.
3. Verify the backup databases are readable.
4. Generate a manifest containing:
   - cascade ID
   - filename
   - file size
   - SHA-256
   - SQLite quick_check result
5. Save the manifest outside the live directory.
6. Record the current Antigravity installation version.
7. Record hashes of every application file that may be modified.

======================================================================
                          PHASE 1
                AUTHORITATIVE INVENTORY
======================================================================

Build an authoritative inventory from:
%USERPROFILE%\.gemini\antigravity-ide\conversations\*.db

For every .db:
1. Verify it is a SQLite database.
2. Run PRAGMA quick_check.
3. Read trajectory_meta and step metadata.
4. Determine the canonical cascade ID.
5. Verify: filename stem == cascade ID.
6. Extract available:
   - title (or first prompt if title unset)
   - timestamps (created, modified)
   - trajectory metadata
   - workspace metadata (workspaceFolderAbsoluteUri)
   - parent conversation information
7. Produce AUTHORITATIVE_CONVERSATION_MANIFEST containing one row per valid current .db.

======================================================================
                          PHASE 2
                UNDERSTAND THE ENCODING
======================================================================

1. Inspect the serialization format in state.vscdb under key:
   antigravityUnifiedStateSync.trajectorySummaries
2. Confirm the schema, map structure, and value encoding.
3. Decode the existing state.
4. Verify that re-encoding without logical changes produces a structurally compatible representation.

======================================================================
                          PHASE 3
                  RECONSTRUCT HISTORY
======================================================================

Build a complete trajectorySummaries map from all authoritative conversation databases.
For EVERY valid current .db:
- key = actual cascade ID
- value = summary derived from actual trajectory metadata

Rules:
- Do NOT use fabricated titles or timestamps.
- Use the same metadata derivation logic Antigravity uses internally.
- The resulting map must contain all real conversation IDs and ZERO orphan IDs.

Run these checks:
- CHECK 1: Every .db has exactly one History entry.
- CHECK 2: Every History entry maps to exactly one .db.
- CHECK 3: No History entry points to a nonexistent conversation.
- CHECK 4: No duplicate cascade IDs.
- CHECK 5: All generated summaries decode cleanly.
- CHECK 6: The known affected conversation (c99ca0b3-a658-48ae-9dba-33eed0571a99) is present.

======================================================================
                          PHASE 4
                   SAFE STATE REPLACEMENT
======================================================================

1. Create a timestamped backup of the current state.vscdb.
2. Stage the reconstructed state.
3. Verify entry count, IDs added, and IDs removed.
4. Atomically commit the reconstructed antigravityUnifiedStateSync.trajectorySummaries into state.vscdb.
5. Record: original file hash, new file hash, timestamp, IDs added, IDs removed.

======================================================================
                 PHASE 5 — PERMANENT FIX
======================================================================

THIS IS THE CRITICAL INVARIANT:
The index must become SELF-HEALING across application restarts.

Architecture:
                    conversation store (*.db)
                               │
                               ▼
                      reconciliation layer
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
            missing summaries      orphan summaries
                 added                 removed
                    │                     │
                    └──────────┬──────────┘
                               ▼
                      trajectorySummaries
                               │
                               ▼
                           History UI

Implementation Options:
- Preferred / Production Path (External Reconciler): A lightweight, idempotent background reconciler (scheduled task / launch script) that runs before Antigravity launch or on logon/hourly. Refuses to run if Antigravity process is active, checks for drift, and safely commits updates.
- In-Process Path: Hook into Antigravity startup sequence before renderer subscription if a stable, non-brittle hook exists.

Permanent Reconciliation Rules:
1. Enumerate valid current conversation databases.
2. Build the authoritative cascade ID set.
3. Load existing trajectory summary state.
4. For each valid DB with no summary: create/reconstruct missing summary.
5. For each summary without a valid DB: remove orphan summary.
6. For existing valid summaries: preserve them.
7. Idempotence: Running twice consecutively MUST result in a no-op.

Important Concurrency & Persistence Rule:
Reconciliation must NEVER race with Antigravity while the IDE is running.
The fix must ensure that shutdown persistence (saveAllTopics) preserves the complete reconciled map.

======================================================================
                       PHASE 6
                  APPLICATION PATCH / DEPLOYMENT
======================================================================

If an external reconciler is deployed:
1. Place script in a dedicated tool path.
2. Configure scheduled task or startup trigger.
3. Test dry-run mode.

If a code patch is applied:
1. Make a backup copy of the original file.
2. Record SHA-256 before and after.
3. Validate syntax and ensure IDE launches cleanly.

======================================================================
                   PHASE 7 — RECOVERY TEST
======================================================================

Start Antigravity.
Verify:
1. History loads without errors.
2. All expected recovered conversations are present.
3. Search can find known missing conversation: c99ca0b3-a658-48ae-9dba-33eed0571a99.
4. Older and recent conversations are visible and searchable.
5. Phantom/orphan IDs are gone.
6. Selecting c99 loads the actual conversation, prompts, and actions.
7. No conversation .db file was modified or deleted.

======================================================================
                 PHASE 8 — RESTART TEST
======================================================================

1. Close Antigravity normally (graceful exit to trigger shutdown persistence).
2. Wait for background process termination.
3. Restart Antigravity.
4. Verify:
   - All recovered conversations remain visible.
   - c99 remains present.
   - Orphan IDs remain absent.
   - Selecting c99 still loads correctly.

IF ENTRIES DISAPPEAR AFTER RESTART, THE FIX HAS FAILED. Investigate shutdown persistence.

======================================================================
               PHASE 9 — NEW CONVERSATION TEST
======================================================================

1. Create a new test conversation in Antigravity with a unique title (e.g. "Test History Persistence").
2. Send multiple prompt messages and receive responses.
3. Verify it appears immediately in History.
4. Close Antigravity normally.
5. Restart Antigravity.
6. Verify the new test conversation remains present and loads properly.

======================================================================
             PHASE 10 — MISSED-EVENT SIMULATION
======================================================================

Verify that if a conversation .db exists on disk without a summary entry in state.vscdb, running the reconciler immediately restores it to History.

======================================================================
                     PHASE 11 — ORPHAN TEST
======================================================================

Verify that if an invalid cascade ID entry exists in the summary map with no corresponding .db on disk, running the reconciler cleanly prunes it.

======================================================================
                  PHASE 12 — FINAL AUDIT & REPORT
======================================================================

Generate a final report detailing:
1. Antigravity version.
2. Backup status & locations.
3. Conversation DB count before and after.
4. Recovered conversation count.
5. Orphan IDs pruned.
6. Confirmation of c99 visibility and loadability.
7. Restart test results.
8. New conversation persistence results.
9. Reconciler trigger / architecture.
10. Rollback instructions.

======================================================================
                     SUCCESS CRITERIA
======================================================================

The task is successful ONLY if all of the following pass:
[ ] All valid conversation DBs have corresponding History entries.
[ ] Zero valid conversation DBs are missing from History.
[ ] Zero orphan History entries remain.
[ ] c99ca0b3-a658-48ae-9dba-33eed0571a99 appears in History and loads properly.
[ ] Older and recent conversations load properly.
[ ] Antigravity restarts cleanly.
[ ] History remains intact after restart.
[ ] New conversations survive restart.
[ ] No conversation DB was deleted or corrupted.
[ ] Rollback instructions are tested and documented.
```
</details>

<details>
<summary><b>🧪 Prompt 2: Verification & Test Suite Prompt (Click to Expand / Collapse)</b></summary>

> 💡 **Quick Copy:** Click the **Copy** button on the top-right of the code block below:

```markdown
You are performing a RIGOROUS AUDIT AND VERIFICATION of the Google Antigravity IDE conversation History fix.

Your task is to independently test, validate, and verify that the conversation History index is fully restored, consistent with the disk store, and permanent across restarts.

Do NOT make destructive changes. Do NOT delete any conversation .db files or brain directories.

Target Antigravity Version: 2.17.x
Conversation Store: %USERPROFILE%\.gemini\antigravity-ide\conversations\*.db
Global State DB: %APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb
History Topic Key: antigravityUnifiedStateSync.trajectorySummaries

Phases to execute:
1. STORE & INDEX INTEGRITY AUDIT: Enumerate .db files, run SQLite quick_check, compare against trajectorySummaries, verify missing = 0 and orphans = 0.
2. RECONCILER IDEMPOTENCE TEST: Verify that running the reconciler a second time results in a clean NO-OP.
3. UI ACCESSIBILITY & SEARCH TEST: Verify search for anchor c99ca0b3-a658-48ae-9dba-33eed0571a99, verify older/recent conversations load full historical turns.
4. SHUTDOWN PERSISTENCE & RESTART TEST: Gracefully exit Antigravity, verify state.vscdb retains all summaries after saveAllTopics, restart and verify 100% retention.
5. NEW CONVERSATION LIFECYCLE TEST: Create a new chat session, verify immediate history addition, close and restart, verify persistence.
6. SCORECARD GENERATION: Produce a markdown audit scorecard with PASS/FAIL status for all test items.
```
</details>

<details>
<summary><b>🔍 Prompt 3: Read-Only Diagnostic Prompt (Click to Expand / Collapse)</b></summary>

> 💡 **Quick Copy:** Click the **Copy** button on the top-right of the code block below:

```markdown
You are performing a READ-ONLY DIAGNOSTIC AUDIT of Google Antigravity IDE conversation History on this machine.

DO NOT make any changes to files, databases, or configuration. All operations must be strictly read-only.

Target paths:
- Conversation databases: %USERPROFILE%\.gemini\antigravity-ide\conversations\*.db
- Global state: %APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb
- History topic key: antigravityUnifiedStateSync.trajectorySummaries

Instructions:
1. Enumerate all .db files in %USERPROFILE%\.gemini\antigravity-ide\conversations\.
2. Run SQLite PRAGMA quick_check on each database. Count how many are healthy.
3. Open state.vscdb in read-only mode and extract the payload for key 'antigravityUnifiedStateSync.trajectorySummaries'.
4. Compute missing .db count and orphan ID count.
5. Check if anchor session 'c99ca0b3-a658-48ae-9dba-33eed0571a99' exists and whether it is indexed.
6. Output a summary table with diagnostic metrics.
```
</details>

---

## 🛡️ Safety Guarantees & Non-Destructive Design

The recovery architecture adheres to strict safety boundaries:

- **Immutable Databases:** The reconciler treats `%USERPROFILE%\.gemini\antigravity-ide\conversations\*.db` as read-only. It **never modifies or deletes conversation databases**.
- **Process Guard:** The reconciler refuses to run while `Antigravity.exe` is running, avoiding SQLite lock collisions and race conditions.
- **Idempotence:** Consecutive runs against a synchronized system perform zero writes (clean NO-OP).
- **Rollback Guarantee:** A timestamped backup of `state.vscdb` is created before any state modification.

---

## 📂 Repository Contents

| File | Description |
| :--- | :--- |
| **[`problem.md`](file:///c:/Users/Anurag/Desktop/antigravity%20chat%20history%20fix/problem.md)** | Technical problem specification, discrepancy metrics, and disproven hypotheses |
| **[`prompts.md`](file:///c:/Users/Anurag/Desktop/antigravity%20chat%20history%20fix/prompts.md)** | Unified prompt library (Diagnostic, Master Fix, Test Suite, Rollback) with copyable code blocks |
| **[`fix_prompt.md`](file:///c:/Users/Anurag/Desktop/antigravity%20chat%20history%20fix/fix_prompt.md)** | Complete 13-phase Master Recovery & Permanent Prevention prompt |
| **[`test_prompt.md`](file:///c:/Users/Anurag/Desktop/antigravity%20chat%20history%20fix/test_prompt.md)** | Dedicated 7-phase Verification, Restart Durability & Lifecycle test prompt |
| **[`Antigravity_History_Forensic_Postmortem_...pdf`](file:///c:/Users/Anurag/Desktop/antigravity%20chat%20history%20fix/Antigravity_History_Forensic_Postmortem_DEEP_WITH_AUTHOR_NOTE_2026-10-03.pdf)** | 21-page exhaustive engineering and forensic postmortem report |

---

## 📖 Key Takeaway

> *"The incident was not fundamentally a case of deleted conversation databases. It was a consistency failure between a healthy durable conversation store and a separately persisted History summary projection."*  
> — **Forensic Postmortem Report, Section 18**
