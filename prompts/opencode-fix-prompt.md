# OpenCode Fix Prompt: Antigravity History Recovery & Invariant Enforcement

> [!IMPORTANT]
> **Instructions for use:** Copy the prompt below directly into **OpenCode** (or your terminal coding agent) to execute the automated repair and permanent invariant reconciliation.

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

The previous investigation established the following.

--------------------------------------------------
A. Conversation store
--------------------------------------------------

Antigravity stores current conversation databases under:

%USERPROFILE%\.gemini\antigravity-ide\conversations\

The current installation contains 58 valid .db conversation files.

The .db filename corresponds to the cascade ID.

The databases were inspected and passed SQLite integrity checking.

The conversation store is therefore the authoritative source for the
existence of current local conversations.

--------------------------------------------------
B. Trajectory store registry
--------------------------------------------------

The trajectory store enumerates:

conversations\*.db

and registers their IDs internally.

This does NOT mean those conversations are automatically loaded into
CascadeManager.

--------------------------------------------------
C. CascadeManager
--------------------------------------------------

There is NO startup bulk hydration of CascadeManager.

The proven load path is:

getCascadeTrajectory
    ↓
trajectoryFetcherImpl.GetCascadeTrajectory
    ↓
CascadeManager.GetTrajectory
    ↓
ensureTrajectoryLoaded
    ↓
CascadeManager.LoadTrajectory
    ↓
Manager.LoadUnsafe
    ↓
processLoadedTrajectory
    ↓
updateStateForLoadedTrajectory

CascadeManager is in-memory.

Every LS restart starts with a fresh registry.

Therefore:

.db exists
    ≠
CascadeManager contains it

A conversation becomes loaded when its cascade ID is actually requested.

--------------------------------------------------
D. History summary state
--------------------------------------------------

The relevant persisted state is:

antigravityUnifiedStateSync.trajectorySummaries

This is NOT an authoritative enumeration of all conversation databases.

It is maintained through frontend summary events.

The relevant update types are:

create
delete
updateAnnotations
updateOptimisticSummary

create is the operation capable of introducing a new cascade ID.

There is no complete enumeration/backfill from:

conversations\*.db

into:

trajectorySummaries

This is the core architectural defect.

--------------------------------------------------
E. Persistence
--------------------------------------------------

The in-memory summary map is updated incrementally.

At application shutdown, the complete current summary topic is serialized
and persisted.

The persisted topic therefore reflects the event-derived in-memory map.

It does NOT perform a read/merge/reconciliation against the conversation
store before writing.

--------------------------------------------------
F. Cleanup
--------------------------------------------------

The cleanup limit is 100.

It is NOT 25.

The cleanup uses the summary's own lastModifiedTime.

The observed 25-entry state is therefore NOT a 25-item History limit.

Do not implement or preserve any artificial 25-item limit.

--------------------------------------------------
G. UI filtering
--------------------------------------------------

The History selector has workspace/metadata filtering, including:

- lastUserInputTime
- trajectoryMetadata.parentConversationId
- workspaces[].workspaceFolderAbsoluteUri

This selector is read-only.

It does NOT explain missing persisted summaries.

Do not "fix" this by disabling the UI filtering unless evidence proves
that filtering is independently wrong.

======================================================================
                     KNOWN AFFECTED STATE
======================================================================

One confirmed missing conversation:

cascade ID:

c99ca0b3-a658-48ae-9dba-33eed0571a99

Its .db exists.

It is a valid SQLite database.

It passed integrity checking.

It contains 329 steps.

It has associated trajectory/project/brain data.

It is missing from normal History/Search.

Another known visible conversation:

686e30bc-6e67-4f84-b395-5b901354f926

Both databases are structurally valid.

The important difference is whether the conversation has an accessible
History summary / has been requested through the normal loading path.

======================================================================
                  PERSISTED INDEX CURRENT STATE
======================================================================

Previous investigation found:

Current .db conversations:
58

Persisted trajectory summary entries:
25

Matching current .db IDs:
1

Orphan IDs:
24

The 24 orphan IDs did not correspond to either:

- current .db
- legacy .pb

Do NOT simply delete the 24 IDs and assume the problem is solved.

The actual goal is to reconstruct the index from the authoritative
conversation databases.

======================================================================
                         PHASE 0
                   BACKUP VERIFICATION
======================================================================

Before modifying anything:

1. Locate the previous 1.42 GB backup.
2. Verify it contains the expected 58 conversation databases.
3. Verify the backup databases are readable.
4. Generate a manifest containing:

   - cascade ID
   - filename
   - file size
   - SHA-256
   - SQLite quick_check result

5. Save the manifest outside the backup.
6. Record the current Antigravity installation version.
7. Record hashes of every application file that may be modified.

If the previous backup cannot be located or verified:

STOP.

Do not attempt repair.

Create a new complete backup first.

======================================================================
                         PHASE 1
               AUTHORITATIVE INVENTORY
======================================================================

Build an authoritative inventory from:

%USERPROFILE%\.gemini\antigravity-ide\conversations\*.db

For every .db:

1. Verify it is a SQLite database.
2. Run PRAGMA quick_check.
3. Read trajectory_meta.
4. Read the trajectory metadata required to construct the History summary.
5. Determine the canonical cascade ID.
6. Verify:

   filename stem == cascade ID

7. Extract available:

   - title
   - timestamps
   - trajectory metadata
   - workspace metadata
   - parent conversation information
   - other fields required by CascadeTrajectorySummary

Do NOT infer values if they are not present.

If a field cannot be reconstructed from the actual DB metadata,
investigate how Antigravity itself derives that field.

Do not fabricate it.

Produce:

AUTHORITATIVE_CONVERSATION_MANIFEST

containing one row per valid current .db.

Expected count:

58

If the count differs:

STOP and explain why before proceeding.

======================================================================
                         PHASE 2
               UNDERSTAND THE ENCODING
======================================================================

The previous investigation decoded the History index format.

Do NOT independently invent a protobuf representation.

Find and reuse the exact encoder/decoder/schema already present in the
installed Antigravity implementation.

Confirm:

- topic name
- protobuf message type
- map structure
- summary row structure
- serialization format
- key/value representation
- profile/storage location

The goal is to produce the exact data format Antigravity itself expects.

Before writing the real state:

1. Decode the existing state.
2. Re-encode it without logical changes.
3. Compare the result structurally.
4. Verify the decoder can read the generated representation.

If the existing encoder can be reused, prefer that over manually writing
protobuf bytes.

======================================================================
                         PHASE 3
                 RECONSTRUCT HISTORY
======================================================================

Build a complete trajectorySummaries map from the 58 authoritative
conversation databases.

For EVERY valid current .db:

- key = actual cascade ID
- value = summary derived from actual trajectory metadata

Do NOT use:

- filesystem mtime as the summary's lastModifiedTime unless that is
  actually how Antigravity derives the field
- fabricated titles
- fabricated timestamps
- fabricated workspace information
- arbitrary defaults when the source metadata exists

Use the same metadata derivation logic Antigravity uses internally.

The resulting map should contain:

58 real conversation IDs

and:

0 orphan IDs.

Before writing:

Run these checks:

CHECK 1:
Every .db has exactly one History entry.

CHECK 2:
Every History entry maps to exactly one .db.

CHECK 3:
No History entry points to a nonexistent conversation.

CHECK 4:
No duplicate cascade IDs.

CHECK 5:
All generated summaries can be decoded by Antigravity's own decoder.

CHECK 6:
The known affected conversation:

c99ca0b3-a658-48ae-9dba-33eed0571a99

is present.

======================================================================
                         PHASE 4
                  SAFE STATE REPLACEMENT
======================================================================

Do NOT directly overwrite the live state yet.

Create:

1. original state backup
2. reconstructed state
3. verification copy

Use the verified encoder to write the reconstructed
antigravityUnifiedStateSync.trajectorySummaries.

Before replacing the live state:

- compare entry count
- compare IDs
- verify no orphan IDs
- verify c99 is present
- verify all 58 DB IDs are present
- verify protobuf decoding

Only after all checks pass should the live state be replaced.

Record:

- original file hash
- new file hash
- timestamp
- entry count
- IDs added
- IDs removed

======================================================================
                 PHASE 5 — PERMANENT FIX
======================================================================

THIS IS THE MOST IMPORTANT PART.

Do NOT stop after repairing the current History.

The current index must become SELF-HEALING.

The desired architecture is:

                    conversation store
                           │
                           ▼
                  reconciliation layer
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
        missing summaries      orphan summaries
             added                removed
                │                     │
                └──────────┬──────────┘
                           ▼
                 trajectorySummaries
                           │
                           ▼
                      History UI

Implementation:
Deploy the standalone background reconciler (src/reconcile_antigravity_history.py)
configured to run before IDE startup or on user logon/hourly.
Ensure zero writes when stores are synchronized (idempotent NO-OP).
```
