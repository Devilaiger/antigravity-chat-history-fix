# Investigation & Recovery Prompt Library

This directory contains the structured prompts used during the forensic reconstruction and validation phases of this investigation.

| Prompt File | Purpose | Risk Level |
| :--- | :--- | :---: |
| **[`diagnostic.md`](file:///c:/Users/Anurag/Desktop/antigravity%20chat%20history%20fix/prompts/diagnostic.md)** | Non-destructive, read-only audit of `.db` files and index disparity. | Read-Only |
| **[`master-recovery.md`](file:///c:/Users/Anurag/Desktop/antigravity%20chat%20history%20fix/prompts/master-recovery.md)** | Step-by-step instructions for manual or agent-assisted index reconciliation. | Moderate |
| **[`verification.md`](file:///c:/Users/Anurag/Desktop/antigravity%20chat%20history%20fix/prompts/verification.md)** | Systematic test suite verifying restart durability and idempotence. | Read-Only |
| **[`emergency-rollback.md`](file:///c:/Users/Anurag/Desktop/antigravity%20chat%20history%20fix/prompts/emergency-rollback.md)** | Safe restoration protocol to restore `state.vscdb` from backups. | Reversible |

> [!NOTE]
> For automated, production-grade recovery without agent prompts, use the standalone reconciler: [`src/reconcile_antigravity_history.py`](file:///c:/Users/Anurag/Desktop/antigravity%20chat%20history%20fix/src/reconcile_antigravity_history.py).
