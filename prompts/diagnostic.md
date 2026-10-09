# Read-Only Diagnostic Prompt

> [!IMPORTANT]
> **Instructions for use:** Copy the prompt below into your AI coding assistant to run a safe, strictly read-only check of your installation.

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
