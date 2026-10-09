# Root Cause Analysis: Antigravity IDE History Index Drift

## 1. Executive Summary

In Google Antigravity IDE (version 2.17.x), conversations frequently disappear from the History sidebar and Search palette even though their underlying SQLite databases remain healthy and fully populated on disk.

The key architectural issue identified is that the persisted History summary state behaves as an event-derived projection, without a corresponding steady-state reconciliation path from the authoritative conversation database set.

---

## 2. Authoritative Store vs. Ephemeral Projection

Antigravity operates with two distinct storage layers:

| Layer | Location | Role & Mechanism |
| :--- | :--- | :--- |
| **Authoritative Store** | `%USERPROFILE%\.gemini\antigravity-ide\conversations\*.db` | Durable SQLite databases storing every turn, step payload, prompt, and tool invocation. Each filename corresponds to a unique cascade ID. |
| **History Projection** | `%APPDATA%\Antigravity IDE\User\globalStorage\state.vscdb` (`antigravityUnifiedStateSync.trajectorySummaries`) | In-memory summary map populated incrementally by frontend `create` events and serialized to `ItemTable` upon shutdown. |

---

## 3. The Failure Mechanism

```
       Durable Store (*.db)
               │
     [ X ] NO RECONCILIATION
           NO STARTUP BACKFILL
               │
               ▼
    Frontend Event Stream ─────► In-Memory Summary Map
                                           │
                                    Shutdown Hook (saveAllTopics)
                                           │
                                           ▼
                                 state.vscdb (Incomplete)
                                           │
                                           ▼
                                    History & Search UI
```

### The Causal Chain:
1. **Unidirectional Event Flow:** History summaries are registered exclusively via in-session UI events.
2. **Missing Reconciliation Path:** When the IDE launches, it seeds `CascadeManager` and `trajectorySummaries` from the previous session's serialized state. It never crawls the conversation directory to verify whether additional `.db` files exist.
3. **Lazy-Load Catch-22:** Antigravity utilizes lazy hydration (`getCascadeTrajectory`). A conversation database is only read from disk when requested by ID. Because unindexed conversations never appear in History or Search, a user cannot click them, and the IDE never invokes `getCascadeTrajectory`.
4. **Shutdown Overwrite Cycle:** During graceful application exit, the IDE serializes its current in-memory map and persists it via `saveAllTopics`. Any past conversation whose event was omitted or lost remains permanently omitted.

---

## 4. Proposed Architectural Invariant

Based on the observed failure and recovery process, we propose the following integrity invariant for the History projection:

> **Proposed Invariant:**  
> *Every valid authoritative conversation database should have a corresponding valid History summary, and every persisted History summary should correspond to an existing authoritative conversation database.*

$$\forall db \in \text{Conversations}_{\text{valid}} \iff \exists ! \, summary \in \text{trajectorySummaries}$$

By establishing a bidirectional reconciliation path, any missing entries are automatically reconstructed from `.db` metadata, and orphan entries pointing to nonexistent files are pruned safely.
