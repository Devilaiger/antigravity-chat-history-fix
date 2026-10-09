# Security Policy

## Data Safety Guarantee
This tooling is designed under defensive systems principles:
1. **Read-Only Data Stores:** Local conversation databases (`%USERPROFILE%\.gemini\antigravity-ide\conversations\*.db`) are opened using SQLite read-only mode (`?mode=ro`). The reconciler never writes to, alters, or truncates conversation databases.
2. **Pre-Mutation State Snapshots:** Before modifying `state.vscdb`, an immutable timestamped backup is generated automatically.
3. **Process Concurrency Protection:** The tool checks process lists and halts if `Antigravity.exe` is running, ensuring that database transactions never collide with the live IDE runtime.
4. **Zero Telemetry / Offline Execution:** The tool operates entirely on local disk with zero external network connectivity or telemetry transmission.

## Reporting a Security Issue
If you discover a vulnerability or potential edge case that could lead to data corruption, please report it via GitHub Issues or contact the maintainers directly.
