# Antigravity History Fix: AI Agent Prompt Library

This document contains the complete, copy-paste-ready prompts for auditing, repairing, testing, and rolling back the Google Antigravity IDE conversation History indexing system.

> [!TIP]
> **One-Click Copy:** Each prompt below is packaged inside a code block. When viewing this file on GitHub or in your editor's Markdown preview, simply click the **Copy** button in the top-right corner of the code block.

---

## 📑 Table of Prompts

1. [Prompt 1: Read-Only Diagnostic & Health Audit](#prompt-1-read-only-diagnostic--health-audit) — Check if your Antigravity installation is affected.
2. [Prompt 2: Master Recovery & Permanent Prevention Fix](#prompt-2-master-recovery--permanent-prevention-fix) — Full 13-phase end-to-end recovery and self-healing fix.
3. [Prompt 3: Verification & Restart Durability Test Suite](#prompt-3-verification--restart-durability-test-suite) — Rigorously test and validate an applied fix.
4. [Prompt 4: Emergency Rollback & State Restoration](#prompt-4-emergency-rollback--state-restoration) — Safely restore original state and backups.

---

## Prompt 1: Read-Only Diagnostic & Health Audit

**Use Case:** Run this first to discover whether you have missing conversations or orphan entries without making any changes to your files.

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
3. Open %APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb in read-only mode (uri=file:...&mode=ro).
4. Extract the payload for key 'antigravityUnifiedStateSync.trajectorySummaries' from ItemTable.
5. Decode the summary entries and extract all indexed cascade IDs.
6. Compare the two sets:
   - Total valid .db files on disk: [A]
   - Total indexed summary IDs in state.vscdb: [B]
   - Valid .db files MISSING from History index (A - B): [Count & list of IDs]
   - Orphan summary entries with NO corresponding .db (B - A): [Count & list of IDs]
7. Check anchor conversation 'c99ca0b3-a658-48ae-9dba-33eed0571a99':
   - Does its .db exist?
   - Is it present in trajectorySummaries?
8. Report the exact findings in a summary table and recommend whether recovery is needed.
```

---

## Prompt 2: Master Recovery & Permanent Prevention Fix

**Use Case:** The primary, complete prompt that recovers missing conversations, prunes phantom entries, and establishes an idempotent self-healing reconciliation boundary.

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

---

## Prompt 3: Verification & Restart Durability Test Suite

**Use Case:** Run this after applying the fix or configuring the reconciler to verify 100% durability, searchability, restart survival, and new conversation persistence.

```markdown
You are performing a RIGOROUS AUDIT AND VERIFICATION of the Google Antigravity IDE conversation History fix.

Your task is to independently test, validate, and verify that the conversation History index is fully restored, consistent with the disk store, and permanent across restarts.

Do NOT make destructive changes. Do NOT delete any conversation .db files or brain directories.

======================================================================
                         TEST SUITE OVERVIEW
======================================================================

Target Antigravity Version: 2.17.x
Conversation Store: %USERPROFILE%\.gemini\antigravity-ide\conversations\*.db
Global State DB: %APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb
History Topic Key: antigravityUnifiedStateSync.trajectorySummaries

You will execute the following 7 verification phases and generate an executive scorecard.

======================================================================
               PHASE 1: STORE & INDEX INTEGRITY AUDIT
======================================================================

Execute an audit while Antigravity is closed:
1. Enumerate all conversation databases in %USERPROFILE%\.gemini\antigravity-ide\conversations\*.db.
2. Run SQLite PRAGMA quick_check on every database. Count total healthy databases.
3. Open state.vscdb in read-only mode and extract the antigravityUnifiedStateSync.trajectorySummaries payload from ItemTable.
4. Decode the summary entries and extract all indexed cascade IDs.
5. Compute the mathematical set differences:
   - Missing IDs: (Valid .db IDs) - (Indexed Summary IDs)
   - Orphan IDs: (Indexed Summary IDs) - (Valid .db IDs)
6. Verify anchor conversations:
   - Check if known missing anchor c99ca0b3-a658-48ae-9dba-33eed0571a99 is present.
   - Check if reference visible anchor 686e30bc-6e67-4f84-b395-5b901354f926 is present.
7. Record the baseline metrics:
   - Total valid .db files: [N]
   - Total indexed summaries: [N]
   - Missing DB count: [N] (Must be 0)
   - Orphan ID count: [N] (Must be 0)

======================================================================
               PHASE 2: RECONCILER IDEMPOTENCE TEST
======================================================================

1. Trigger the reconciliation mechanism (or run the reconciler script in dry-run/apply mode).
2. Verify that when run against an already-reconciled state:
   - Drift detected: 0
   - DB writes performed: 0
   - Result: Clean NO-OP
3. Ensure no database file mtimes or contents are modified.

======================================================================
               PHASE 3: UI ACCESSIBILITY & SEARCH TEST
======================================================================

Launch Antigravity IDE and inspect the user interface:
1. Open the Conversation History list. Verify the conversation count matches expectations.
2. In the Search bar, search for anchor session: c99ca0b3-a658-48ae-9dba-33eed0571a99.
   - Verify it appears in results.
   - Click to open it.
   - Confirm that historical turns, user prompts, agent responses, and tool calls load completely.
3. Search for at least 3 older conversations and 3 recent conversations. Confirm all open cleanly.
4. Verify workspace filtering behavior:
   - Note which conversations are scoped to the active workspace vs global.
   - Confirm that workspace filtering does not cause underlying summaries to be deleted.

======================================================================
               PHASE 4: SHUTDOWN PERSISTENCE & RESTART TEST
======================================================================

This is the CRITICAL PERSISTENCE GATE:
1. Close Antigravity gracefully (do not forcefully kill - allow normal window close to trigger shutdown hooks).
2. Wait 5 seconds for background processes (Antigravity.exe, language servers) to fully terminate.
3. Open state.vscdb read-only and inspect antigravityUnifiedStateSync.trajectorySummaries immediately after shutdown.
   - Verify that shutdown serialization did NOT overwrite the reconciled state with an incomplete in-memory snapshot.
   - Verify the entry count has not regressed.
   - Verify c99ca0b3-a658-48ae-9dba-33eed0571a99 remains present in state.vscdb.
4. Relaunch Antigravity.
5. Re-check the History UI. Confirm that all recovered sessions remain listed and selectable.

======================================================================
               PHASE 5: NEW CONVERSATION LIFECYCLE TEST
======================================================================

Test normal incremental chat operation:
1. Start a new conversation in Antigravity.
2. Title it: "VERIFICATION_TEST_CONVERSATION_[TIMESTAMP]".
3. Exchange at least 2 prompt-response turns with the assistant.
4. Verify the new conversation immediately appears in the History list.
5. Note its generated cascade ID. Confirm a corresponding .db file exists in %USERPROFILE%\.gemini\antigravity-ide\conversations\.
6. Close Antigravity normally.
7. Relaunch Antigravity.
8. Confirm both the new test conversation AND all previously recovered conversations remain present and functional.

======================================================================
               PHASE 6: FAULT-INJECTION DRIFT TEST (OPTIONAL)
======================================================================

If a disposable staging copy is available:
1. Inject simulated drift:
   - Remove 1 valid summary entry from state.vscdb.
   - Add 1 phantom summary entry with a dummy UUID.
2. Run the reconciler.
3. Verify convergence:
   - The missing valid conversation is re-added.
   - The phantom orphan entry is pruned.
   - Final state converges back to 100% store parity.

======================================================================
               PHASE 7: FINAL SCORECARD & AUDIT REPORT
======================================================================

Produce a markdown scorecard with the following format:

| Test Item | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :---: |
| SQLite DB Health Check | All DBs quick_check OK | [Result] | PASS / FAIL |
| Missing Conversations | 0 missing | [Result] | PASS / FAIL |
| Orphan Summary Entries | 0 orphans | [Result] | PASS / FAIL |
| Anchor c99 Visibility | Searchable & loads turns | [Result] | PASS / FAIL |
| Graceful Shutdown Retention | Whole-map survives saveAllTopics | [Result] | PASS / FAIL |
| Cold Restart Durability | 100% entries retained after restart | [Result] | PASS / FAIL |
| New Conversation Creation | Appears & persists across restart | [Result] | PASS / FAIL |
| Reconciler Idempotence | Consecutive run is no-op | [Result] | PASS / FAIL |

FINAL VERDICT: [PASS / FAIL]
```

---

## Prompt 4: Emergency Rollback & State Restoration

**Use Case:** Use this if you need to revert changes back to the exact pre-repair state.

```markdown
You are performing a SAFE, NON-DESTRUCTIVE ROLLBACK of Google Antigravity IDE state to a verified pre-repair snapshot.

Rules:
- Antigravity MUST be closed before touching any state files.
- NEVER delete conversation databases in %USERPROFILE%\.gemini\antigravity-ide\conversations\.
- Only restore state.vscdb and any modified application files from verified backups.

Instructions:
1. Verify Antigravity is closed using PowerShell:
   Get-Process Antigravity -ErrorAction SilentlyContinue
   If running, wait or request the user to close it.
2. Locate the pre-repair backup snapshot (e.g. state.vscdb.backup or timestamped recovery folder).
3. Verify the backup's integrity using SQLite PRAGMA quick_check.
4. Replace the live state.vscdb with the verified pre-repair copy.
5. If any application files or scheduled tasks were installed:
   - Revert modified JS bundles to their original unpatched copies.
   - Disable or remove the scheduled task:
     Unregister-ScheduledTask -TaskName 'Antigravity History Reconciler' -Confirm:$false
6. Verify Antigravity launches cleanly and returns to the pre-repair state without errors.
```
