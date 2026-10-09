# Emergency Rollback & Restoration Prompt

> [!IMPORTANT]
> **Instructions for use:** Copy the prompt below into your AI coding assistant to safely revert changes and restore a previous backup of `state.vscdb`.

```markdown
You are performing an EMERGENCY ROLLBACK for Google Antigravity IDE global state.

Target paths:
- Global storage DB: %APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb
- Backups directory: %APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb.backup_*

Instructions:
1. Verify Antigravity is closed. Refuse execution if Antigravity.exe is active.
2. Locate the most recent valid pre-mutation backup: state.vscdb.backup_*.
3. Verify the backup is a valid SQLite file (PRAGMA quick_check = ok).
4. Create a safety snapshot of the current state.vscdb before overwriting.
5. Restore the verified backup by copying it over state.vscdb.
6. Verify file integrity and size match the backup.
7. Confirm clean rollback completion.
```
