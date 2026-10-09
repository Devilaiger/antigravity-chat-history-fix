# Kilo Code CLI Fix Prompt: Antigravity History Recovery & Invariant Enforcement

> [!IMPORTANT]
> **Instructions for use:** Copy the prompt below directly into **Kilo Code CLI** (`kilo`) to execute the recovery and permanent prevention fix.

```markdown
We are performing the FINAL RECOVERY + PERMANENT PREVENTION FIX for a
Google Antigravity IDE conversation History/indexing bug.

This is NOT a request for another forensic report.

The objective is to:

1. Recover ALL currently valid conversations into Antigravity History.
2. Remove all orphan/phantom History entries.
3. Make History automatically reconcile itself with the real conversation store.
4. Ensure missing frontend summary events can NEVER permanently hide an
   otherwise valid conversation during normal operation.
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

If any step is ambiguous, STOP and investigate the existing implementation
before modifying anything.

======================================================================
                     CURRENT KNOWN STATE
======================================================================

Antigravity version:

2.17.0

Antigravity is currently CLOSED.

A previous Work/Codex session already performed a read-only forensic
investigation and created a complete backup.

The backup contains:

- 58 current conversation databases
- active/global profile state
- approximately 1.42 GB of data

The conversation store is:

%USERPROFILE%\.gemini\antigravity-ide\conversations\

Global application state is:

%APPDATA%\Antigravity IDE\User\globalStorage\

DO NOT assume the backup is valid merely because the previous agent said so.

First:

1. Locate the backup.
2. Verify that it exists.
3. Verify the number of conversation databases in the backup.
4. Verify the backup contains the relevant global/profile state.
5. Verify the backup is readable.
6. Record its location.
7. Treat the backup as the immutable rollback source.

Do not modify the backup.

======================================================================
                    ESTABLISHED ARCHITECTURE
======================================================================

The previous investigation established the following:

A. Conversation store:
   Antigravity stores current conversation databases under:
   %USERPROFILE%\.gemini\antigravity-ide\conversations\
   The current installation contains 58 valid .db conversation files.
   The .db filename corresponds to the cascade ID.
   The databases passed SQLite integrity checking.
   The conversation store is the authoritative source.

B. CascadeManager:
   There is NO startup bulk hydration of CascadeManager.
   The proven load path is:
   getCascadeTrajectory -> trajectoryFetcherImpl.GetCascadeTrajectory -> CascadeManager.GetTrajectory -> ensureTrajectoryLoaded -> CascadeManager.LoadTrajectory -> Manager.LoadUnsafe -> processLoadedTrajectory -> updateStateForLoadedTrajectory.
   CascadeManager is in-memory. Every LS restart starts with a fresh registry.
   Therefore: .db exists != CascadeManager contains it.
   A conversation becomes loaded when its cascade ID is actually requested.

C. History summary state:
   The relevant persisted state is:
   antigravityUnifiedStateSync.trajectorySummaries
   Maintained exclusively through frontend summary events (create, delete, updateAnnotations).
   There is no complete enumeration/backfill from conversations\*.db into trajectorySummaries.
   This is the core architectural defect.

D. Persistence:
   At application shutdown, the complete in-memory summary topic is serialized and persisted (saveAllTopics).
   It does NOT perform a read/merge/reconciliation against the conversation store before writing.

======================================================================
                     KNOWN AFFECTED STATE
======================================================================

Confirmed missing conversation anchor:
cascade ID: c99ca0b3-a658-48ae-9dba-33eed0571a99
- .db exists and passes integrity check
- Contains 329 steps
- Missing from normal History/Search

Comparison visible session:
cascade ID: 686e30bc-6e67-4f84-b395-5b901354f926

======================================================================
                         PHASE 0 - 5
                     EXECUTION ROADMAP
======================================================================

1. Phase 0: Backup verification (verify 58 DBs, size, readability).
2. Phase 1: Authoritative inventory (read trajectory_meta, steps, canonical cascade ID).
3. Phase 2: Encoding verification (decode/re-encode trajectorySummaries payload).
4. Phase 3: Reconstruct history (map all 58 valid DBs, 0 orphans, verify anchor c99).
5. Phase 4: Atomic state replacement (timestamped backup, commit to ItemTable).
6. Phase 5: Self-healing architecture (deploy reconciler in src/reconcile_antigravity_history.py).
```
