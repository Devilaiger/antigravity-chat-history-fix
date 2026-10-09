# Investigation & Recovery Prompt Library

This directory contains the verified, production-tested prompts used across different AI coding agents and CLI environments to audit, recover, and validate Google Antigravity IDE conversation history.

---

## 🤖 Agent-Specific Fix Prompts

| Agent / Environment | Prompt File | Description |
| :--- | :--- | :--- |
| **OpenCode** | [`opencode-fix-prompt.md`](opencode-fix-prompt.md) | Tailored for OpenCode agent workflows with process checking and safe state reconciliation. |
| **Kilo Code CLI** | [`kilo-code-cli-fix-prompt.md`](kilo-code-cli-fix-prompt.md) | Formatted for terminal CLI execution (`kilo`) with PowerShell command sequences. |
| **OpenAI Codex** | [`codex-fix-prompt.md`](codex-fix-prompt.md) | Structured for Codex and CLI agent environments. |
| **Universal / Claude Code / Antigravity** | [`master-recovery.md`](master-recovery.md) | Comprehensive 13-phase universal recovery prompt for advanced agentic workflows. |

---

## 🔍 Diagnostic & Lifecycle Test Prompts

| Purpose | Prompt File | Risk Level | Description |
| :--- | :--- | :---: | :--- |
| **Read-Only Audit** | [`diagnostic.md`](diagnostic.md) | Read-Only | Checks `.db` health and measures discrepancy without mutating files. |
| **Test & Durability** | [`verification.md`](verification.md) | Read-Only | Runs multi-phase restart survival, idempotence, and lifecycle tests. |
| **Emergency Revert** | [`emergency-rollback.md`](emergency-rollback.md) | Reversible | Restores `state.vscdb` cleanly from a pre-mutation timestamped backup. |

> [!NOTE]
> For automated, production-grade recovery without agent prompts, use the standalone Python CLI tool: [`src/reconcile_antigravity_history.py`](../src/reconcile_antigravity_history.py).
