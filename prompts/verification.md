# Verification & Durability Test Suite Prompt

> [!IMPORTANT]
> **Instructions for use:** Copy the prompt below into your AI coding assistant to independently test, audit, and validate an applied History fix or reconciler run.

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
