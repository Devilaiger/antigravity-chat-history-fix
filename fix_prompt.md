# Antigravity History Recovery & Permanent Prevention Fix Prompt

> [!IMPORTANT]
> **Instructions for use:**
> Click the **Copy** button on the top-right of the code block below to copy the complete, uncut prompt. Then paste it directly into your AI coding assistant (Antigravity, Claude Code, Codex, OpenCode, or Cursor).

---

## 📋 Copyable Prompt (Click Copy in Code Block)

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

## 🔍 Detailed Phase Breakdown (Human-Readable)

### Phase 0: Backup Verification
Always create immutable copies of `%USERPROFILE%\.gemini\antigravity-ide\conversations\` and `%APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb` before initiating repairs.

### Phase 1–4: Forensic Rebuild
1. **Catalog:** Enumerate every `.db` file using `sqlite3`. Verify integrity with `PRAGMA quick_check`.
2. **Derive:** Extract canonical `cascade_id`, `trajectory_id`, `created_time`, `last_modified_time`, workspace URI, and step counts.
3. **Re-encode:** Construct the `antigravityUnifiedStateSync.trajectorySummaries` blob adhering to the schema.
4. **Commit:** Safely update `ItemTable` in `state.vscdb` while Antigravity is closed.

### Phase 5–6: Self-Healing Architecture
Rather than fragile modifications to minified vendor bundles (`workbench.desktop.main.js`), deploy an **External Integrity Boundary**:
- Runs via Windows Scheduled Task at user logon and hourly.
- Refuses execution if `Antigravity.exe` is currently running (prevents SQLite locking and write races).
- Compares `.db` files against `state.vscdb` and only executes a commit if genuine drift is detected.

### Phase 7–12: Lifecycle Verification Suite
- **Recovery:** Confirm missing sessions (including anchor `c99ca0b3-a658-48ae-9dba-33eed0571a99`) render in the UI.
- **Restart Survival:** Verify that graceful shutdown and restart does not overwrite the reconciled index.
- **Incremental Creation:** Confirm normal chat operations continue to register new conversations seamlessly.