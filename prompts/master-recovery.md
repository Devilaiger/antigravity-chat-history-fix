# Master Recovery & Permanent Prevention Prompt

> [!IMPORTANT]
> **Instructions for use:** Copy the prompt below into your AI coding assistant (Antigravity, Claude Code, Codex, or Cursor) to execute an automated recovery and configure the self-healing reconciliation boundary.

```markdown
You are performing the FINAL RECOVERY + PERMANENT PREVENTION FIX for the Google Antigravity IDE conversation History/indexing bug.

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
- fabricate titles or timestamps
- assume a 25-conversation limit
- overwrite files before creating backups
- modify anything until the current backup is verified
- claim success until the restart tests pass

Do not make destructive changes.

======================================================================
                      CURRENT KNOWN STATE
======================================================================

Antigravity version: 2.17.x
Antigravity is currently CLOSED.

Conversation store:
%USERPROFILE%\.gemini\antigravity-ide\conversations\

Global application state:
%APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb

Target missing conversation anchor:
cascade ID: c99ca0b3-a658-48ae-9dba-33eed0571a99

======================================================================
                      EXECUTION PHASES
======================================================================

1. BACKUP: Create timestamped backup of state.vscdb.
2. SCAN: Enumerate %USERPROFILE%\.gemini\antigravity-ide\conversations\*.db and run PRAGMA quick_check.
3. AUDIT: Read ItemTable antigravityUnifiedStateSync.trajectorySummaries from state.vscdb.
4. RECONCILE: Backfill missing valid summaries and prune orphan entries.
5. VALIDATE: Verify anchor c99ca0b3-a658-48ae-9dba-33eed0571a99 is present.
6. RESTART TEST: Verify state persists cleanly across cold IDE restart.
```
