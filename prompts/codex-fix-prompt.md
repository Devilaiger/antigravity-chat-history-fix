# OpenAI Codex Fix Prompt: Antigravity History Recovery & Synchronization

> [!IMPORTANT]
> **Instructions for use:** Copy the prompt below directly into **OpenAI Codex** (or your terminal coding assistant) to execute the recovery workflow.

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

Antigravity version: 2.17.0
Antigravity is currently CLOSED.

The conversation store is:
%USERPROFILE%\.gemini\antigravity-ide\conversations\

Global application state is:
%APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb

Target missing conversation anchor:
cascade ID: c99ca0b3-a658-48ae-9dba-33eed0571a99 (329 steps, intact SQLite database)

Reference visible conversation:
cascade ID: 686e30bc-6e67-4f84-b395-5b901354f926

======================================================================
                         PHASE 0 - 5
                     EXECUTION INSTRUCTIONS
======================================================================

1. Phase 0: Backup Verification
   - Create or verify immutable backup of state.vscdb before making any change.

2. Phase 1: Authoritative Inventory
   - Enumerate all *.db in %USERPROFILE%\.gemini\antigravity-ide\conversations\.
   - Run PRAGMA quick_check on each.
   - Extract canonical cascade ID and title/prompt from steps table.

3. Phase 2: Encoding Verification
   - Read and decode antigravityUnifiedStateSync.trajectorySummaries from ItemTable in state.vscdb.

4. Phase 3: Reconstruct History
   - Build a complete summary map for all valid conversation DBs (0 orphans).
   - Ensure anchor c99ca0b3-a658-48ae-9dba-33eed0571a99 is present.

5. Phase 4: Safe State Replacement
   - Atomically commit the reconstructed trajectorySummaries payload into ItemTable.

6. Phase 5: Permanent Self-Healing Fix
   - Verify deployment of the external reconciler (src/reconcile_antigravity_history.py).
   - Confirm consecutive executions result in a clean NO-OP (idempotent).
```
