# Antigravity History Fix: Verification & Test Suite Prompt

> [!IMPORTANT]
> **Instructions for use:**
> Click the **Copy** button on the top-right of the code block below to copy this verification prompt. Use this prompt with an AI assistant to rigorously audit, test, and validate an applied History fix or reconciler installation.

---

## 📋 Copyable Test Prompt (Click Copy in Code Block)

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

## 🔍 Test Execution Guidelines

1. **Safety First:** Never run tests that write to `state.vscdb` while `Antigravity.exe` is running. Always verify process termination using `Get-Process Antigravity -ErrorAction SilentlyContinue`.
2. **Anchor Session:** `c99ca0b3-a658-48ae-9dba-33eed0571a99` serves as the primary test anchor because it represents a large, multi-turn (329 steps) historical conversation that was previously confirmed missing despite a healthy SQLite database.
3. **Shutdown Verification:** Antigravity commits its in-memory state during the `saveAllTopics` lifecycle event at application termination. Testing that the index survives shutdown and restart proves that the fix is permanent and self-healing.