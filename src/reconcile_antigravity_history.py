#!/usr/bin/env python3
"""
Antigravity Conversation History Reconciler
===========================================
Investigates and reconciles Antigravity IDE History summaries with the authoritative
local conversation database store.

Authoritative Store:  %USERPROFILE%/.gemini/antigravity-ide/conversations/*.db
History Projection:   %APPDATA%/Antigravity IDE/User/globalStorage/state.vscdb
                      [ItemTable: antigravityUnifiedStateSync.trajectorySummaries]

Safety Invariants:
1. Conversation .db files are strictly read-only and never modified or deleted.
2. Refuses to run if Antigravity is running (prevents write races & locking).
3. Creates an immutable timestamped backup of state.vscdb before any state mutation.
4. Fully idempotent: consecutive runs on a synchronized state perform 0 writes.
"""

from __future__ import annotations

import argparse
import base64
import csv
import datetime
import hashlib
import json
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


STATE_TOPIC_KEY = "antigravityUnifiedStateSync.trajectorySummaries"
DEFAULT_CONVERSATIONS_DIR_REL = Path(".gemini") / "antigravity-ide" / "conversations"
DEFAULT_GLOBAL_STORAGE_REL = Path("Antigravity IDE") / "User" / "globalStorage" / "state.vscdb"


@dataclass
class ConversationMetadata:
    cascade_id: str
    db_path: str
    is_valid_sqlite: bool
    quick_check_status: str
    file_size_bytes: int
    step_count: int
    title: str
    created_time_ms: int
    last_modified_time_ms: int
    workspace_uri: Optional[str] = None
    trajectory_id: Optional[str] = None


@dataclass
class ReconciliationReport:
    timestamp: str
    conversations_scanned: int
    valid_dbs_count: int
    corrupted_dbs_count: int
    persisted_summaries_count: int
    missing_summary_ids: List[str]
    orphan_summary_ids: List[str]
    valid_matching_ids: List[str]
    actions_taken: List[str]
    backup_path: Optional[str] = None
    is_idempotent: bool = True
    dry_run: bool = True


def get_default_conversations_dir() -> Path:
    home = Path.home()
    return home / DEFAULT_CONVERSATIONS_DIR_REL


def get_default_state_db_path() -> Path:
    if platform.system() == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / DEFAULT_GLOBAL_STORAGE_REL
    elif platform.system() == "Darwin":
        home = Path.home()
        return home / "Library" / "Application Support" / DEFAULT_GLOBAL_STORAGE_REL
    home = Path.home()
    return home / ".config" / DEFAULT_GLOBAL_STORAGE_REL


def is_antigravity_running() -> bool:
    """Check whether Antigravity process is currently active."""
    system = platform.system()
    try:
        if system == "Windows":
            out = subprocess.check_output(
                ["tasklist", "/FI", "IMAGENAME eq Antigravity.exe", "/FO", "CSV", "/NH"],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            return "Antigravity.exe" in out
        else:
            out = subprocess.check_output(["pgrep", "-i", "antigravity"], stderr=subprocess.DEVNULL, text=True)
            return bool(out.strip())
    except Exception:
        return False


def inspect_conversation_db(db_path: Path) -> ConversationMetadata:
    """Read a conversation database without modifying it. Verifies integrity and extracts metadata."""
    file_size = db_path.stat().st_size
    filename_cascade_id = db_path.stem
    uri_path = f"file:{db_path.as_posix()}?mode=ro"

    is_valid = True
    quick_check = "ok"
    step_count = 0
    title = f"Conversation {filename_cascade_id[:8]}"
    created_ms = int(db_path.stat().st_ctime * 1000)
    modified_ms = int(db_path.stat().st_mtime * 1000)
    workspace_uri = None
    trajectory_id = None

    try:
        conn = sqlite3.connect(uri_path, uri=True, timeout=5.0)
        cur = conn.cursor()

        # 1. Integrity check
        cur.execute("PRAGMA quick_check;")
        row = cur.fetchone()
        if not row or row[0].lower() != "ok":
            quick_check = row[0] if row else "failed"
            is_valid = False

        # 2. Extract trajectory meta
        try:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trajectory_meta';")
            if cur.fetchone():
                cur.execute("SELECT trajectory_id, cascade_id FROM trajectory_meta LIMIT 1;")
                meta_row = cur.fetchone()
                if meta_row:
                    trajectory_id = meta_row[0]
                    if meta_row[1] and len(meta_row[1]) > 10:
                        filename_cascade_id = meta_row[1]
        except Exception:
            pass

        # 3. Extract step count and extract initial user prompt / title
        try:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='steps';")
            if cur.fetchone():
                cur.execute("SELECT count(*) FROM steps;")
                cnt_row = cur.fetchone()
                step_count = cnt_row[0] if cnt_row else 0

                cur.execute(
                    "SELECT step_payload FROM steps WHERE step_type = 1 OR step_payload IS NOT NULL ORDER BY idx ASC LIMIT 5;"
                )
                for step_row in cur.fetchall():
                    payload = step_row[0]
                    if payload:
                        text_match = None
                        if isinstance(payload, bytes):
                            try:
                                decoded_str = payload.decode("utf-8", errors="ignore")
                                prompts = re.findall(r"[\x20-\x7E]{5,100}", decoded_str)
                                if prompts:
                                    text_match = prompts[0].strip()
                            except Exception:
                                pass
                        elif isinstance(payload, str):
                            text_match = payload.strip()
                        if text_match and len(text_match) > 3:
                            title = text_match[:80]
                            break
        except Exception:
            pass

        conn.close()
    except Exception as exc:
        is_valid = False
        quick_check = f"Error: {exc}"

    return ConversationMetadata(
        cascade_id=filename_cascade_id,
        db_path=str(db_path.resolve()),
        is_valid_sqlite=is_valid,
        quick_check_status=quick_check,
        file_size_bytes=file_size,
        step_count=step_count,
        title=title,
        created_time_ms=created_ms,
        last_modified_time_ms=modified_ms,
        workspace_uri=workspace_uri,
        trajectory_id=trajectory_id,
    )


class StateStoreHandler:
    """Handles safe read/write operations against global storage state.vscdb."""

    def __init__(self, state_db_path: Path):
        self.state_db_path = state_db_path

    def exists(self) -> bool:
        return self.state_db_path.exists()

    def create_backup(self, backup_dir: Optional[Path] = None) -> Path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        target_dir = backup_dir or self.state_db_path.parent
        target_dir.mkdir(parents=True, exist_ok=True)
        backup_file = target_dir / f"state.vscdb.backup_{timestamp}"
        shutil.copy2(self.state_db_path, backup_file)
        return backup_file

    def read_summaries_raw(self) -> Optional[Tuple[str, Any]]:
        """Read value for antigravityUnifiedStateSync.trajectorySummaries from ItemTable."""
        if not self.exists():
            return None
        uri = f"file:{self.state_db_path.as_posix()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, timeout=5.0)
        cur = conn.cursor()
        cur.execute("SELECT value FROM ItemTable WHERE key = ?", (STATE_TOPIC_KEY,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        raw_val = row[0]
        return ("raw", raw_val)

    def extract_summary_keys(self, raw_val: str) -> Set[str]:
        """Extract cascade IDs from persisted trajectorySummaries payload.

        Handles both JSON-serialized dictionaries and base64-encoded protobuf envelopes.
        """
        keys: Set[str] = set()
        if not raw_val:
            return keys

        # Format 1: Direct JSON dictionary
        try:
            data = json.loads(raw_val)
            if isinstance(data, dict):
                return set(data.keys())
        except Exception:
            pass

        # Format 2: Base64 protobuf string (common in unified state sync)
        try:
            decoded = base64.b64decode(raw_val)
            uuid_regex = re.compile(
                rb"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
            )
            for m in uuid_regex.finditer(decoded):
                keys.add(m.group(0).decode("ascii"))
        except Exception:
            pass

        # Format 3: Raw UUID extraction fallback
        raw_bytes = raw_val.encode("utf-8", errors="ignore")
        uuid_regex = re.compile(
            rb"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
        )
        for m in uuid_regex.finditer(raw_bytes):
            keys.add(m.group(0).decode("ascii"))

        return keys

    def write_summaries(self, updated_raw_val: str) -> None:
        """Atomically update the topic in ItemTable."""
        conn = sqlite3.connect(str(self.state_db_path), timeout=10.0)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO ItemTable (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value;
            """,
            (STATE_TOPIC_KEY, updated_raw_val),
        )
        conn.commit()
        conn.close()


def generate_synthetic_summary_dict(
    existing_summaries_dict: Dict[str, Any],
    metadata_list: List[ConversationMetadata],
    prune_orphans: bool = True,
) -> Tuple[Dict[str, Any], List[str], List[str]]:
    """Construct a clean, reconciled JSON summary dictionary.

    Returns:
        (reconciled_dict, added_ids, removed_ids)
    """
    reconciled = dict(existing_summaries_dict)
    valid_ids = {m.cascade_id for m in metadata_list if m.is_valid_sqlite}
    added_ids: List[str] = []
    removed_ids: List[str] = []

    # 1. Add missing summaries
    for meta in metadata_list:
        if not meta.is_valid_sqlite:
            continue
        cid = meta.cascade_id
        if cid not in reconciled:
            reconciled[cid] = {
                "cascadeId": cid,
                "title": meta.title,
                "stepCount": meta.step_count,
                "createdTime": meta.created_time_ms,
                "lastModifiedTime": meta.last_modified_time_ms,
                "trajectoryId": meta.trajectory_id or cid,
                "workspaceUri": meta.workspace_uri,
            }
            added_ids.append(cid)

    # 2. Prune orphan summaries
    if prune_orphans:
        current_keys = list(reconciled.keys())
        for k in current_keys:
            if k not in valid_ids:
                del reconciled[k]
                removed_ids.append(k)

    return reconciled, added_ids, removed_ids


def reconcile_history(
    conversations_dir: Path,
    state_db_path: Path,
    dry_run: bool = True,
    prune_orphans: bool = True,
    backup_dir: Optional[Path] = None,
    force: bool = False,
) -> ReconciliationReport:
    """Main reconciliation routine."""
    timestamp = datetime.datetime.now().isoformat()

    # Process guard
    if not force and is_antigravity_running():
        raise RuntimeError(
            "Antigravity IDE is currently running. Please close Antigravity before reconciling "
            "to prevent write races and SQLite locking, or pass --force."
        )

    if not conversations_dir.exists():
        raise FileNotFoundError(f"Conversations directory does not exist: {conversations_dir}")

    # Step 1: Scan all conversation databases
    db_files = sorted(list(conversations_dir.glob("*.db")))
    metadata_list: List[ConversationMetadata] = []
    valid_ids: Set[str] = set()
    corrupted_count = 0

    for db_path in db_files:
        meta = inspect_conversation_db(db_path)
        metadata_list.append(meta)
        if meta.is_valid_sqlite:
            valid_ids.add(meta.cascade_id)
        else:
            corrupted_count += 1

    # Step 2: Read current index state
    state_handler = StateStoreHandler(state_db_path)
    current_indexed_keys: Set[str] = set()
    raw_payload_tuple = state_handler.read_summaries_raw()
    raw_val = raw_payload_tuple[1] if raw_payload_tuple else None

    is_json_format = False
    existing_json_dict: Dict[str, Any] = {}

    if raw_val:
        try:
            parsed = json.loads(raw_val)
            if isinstance(parsed, dict):
                is_json_format = True
                existing_json_dict = parsed
        except Exception:
            pass
        current_indexed_keys = state_handler.extract_summary_keys(raw_val)

    # Step 3: Compute drift
    missing_ids = sorted(list(valid_ids - current_indexed_keys))
    orphan_ids = sorted(list(current_indexed_keys - valid_ids))
    matching_ids = sorted(list(valid_ids & current_indexed_keys))
    actions_taken: List[str] = []
    backup_path_str = None
    is_idempotent = len(missing_ids) == 0 and len(orphan_ids) == 0

    # Step 4: Execute reconciliation if not dry-run
    if not dry_run:
        if not is_idempotent:
            backup_file = state_handler.create_backup(backup_dir)
            backup_path_str = str(backup_file.resolve())
            actions_taken.append(f"Created pre-mutation backup at: {backup_path_str}")

            if is_json_format or not raw_val:
                reconciled_dict, added, removed = generate_synthetic_summary_dict(
                    existing_json_dict, metadata_list, prune_orphans=prune_orphans
                )
                state_handler.write_summaries(json.dumps(reconciled_dict, indent=2))
                actions_taken.append(f"Updated ItemTable: +{len(added)} added, -{len(removed)} orphans pruned")
            else:
                # If existing is encoded in a binary envelope, we inject reconstructed JSON
                # or maintain format parity
                reconciled_dict, added, removed = generate_synthetic_summary_dict(
                    {}, metadata_list, prune_orphans=prune_orphans
                )
                state_handler.write_summaries(json.dumps(reconciled_dict, indent=2))
                actions_taken.append(f"Reconstructed trajectorySummaries JSON: +{len(added)} added, -{len(removed)} orphans pruned")
        else:
            actions_taken.append("State is already synchronized (0 missing, 0 orphans). Clean NO-OP.")

    return ReconciliationReport(
        timestamp=timestamp,
        conversations_scanned=len(db_files),
        valid_dbs_count=len(valid_ids),
        corrupted_dbs_count=corrupted_count,
        persisted_summaries_count=len(current_indexed_keys),
        missing_summary_ids=missing_ids,
        orphan_summary_ids=orphan_ids,
        valid_matching_ids=matching_ids,
        actions_taken=actions_taken,
        backup_path=backup_path_str,
        is_idempotent=is_idempotent,
        dry_run=dry_run,
    )


def export_manifest_csv(metadata_list: List[ConversationMetadata], output_path: Path) -> None:
    """Exports conversation catalog to a standard CSV manifest."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "cascade_id",
            "db_path",
            "is_valid_sqlite",
            "quick_check_status",
            "file_size_bytes",
            "step_count",
            "title",
            "created_time_ms",
            "last_modified_time_ms",
            "workspace_uri",
            "trajectory_id",
        ])
        for m in metadata_list:
            writer.writerow([
                m.cascade_id,
                m.db_path,
                m.is_valid_sqlite,
                m.quick_check_status,
                m.file_size_bytes,
                m.step_count,
                m.title,
                m.created_time_ms,
                m.last_modified_time_ms,
                m.workspace_uri or "",
                m.trajectory_id or "",
            ])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Antigravity IDE Conversation History Reconciler and Integrity Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Perform read-only diagnostic check and report drift without modifying state.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply reconciliation changes: backfill missing summaries and prune orphans.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Simulate reconciliation and display planned actions (default mode if --apply is omitted).",
    )
    parser.add_argument(
        "--conversations-dir",
        type=Path,
        default=get_default_conversations_dir(),
        help="Path to conversations directory containing *.db files.",
    )
    parser.add_argument(
        "--state-db",
        type=Path,
        default=get_default_state_db_path(),
        help="Path to state.vscdb SQLite database.",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help="Directory to save state.vscdb backups before state modification.",
    )
    parser.add_argument(
        "--manifest-out",
        type=Path,
        default=None,
        help="Optional path to output authoritative inventory manifest CSV.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Bypass process running guard (use with caution).",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed diagnostic information.",
    )

    args = parser.parse_args()

    dry_run = not args.apply

    print("=" * 70)
    print(" Antigravity Conversation History Reconciler & Integrity Tool")
    print("=" * 70)
    print(f" Mode: {'DRY RUN / CHECK' if dry_run else 'APPLY (MUTATING)'}")
    print(f" Conversations Store: {args.conversations_dir}")
    print(f" State Store:        {args.state_db}")
    print("=" * 70)

    try:
        report = reconcile_history(
            conversations_dir=args.conversations_dir,
            state_db_path=args.state_db,
            dry_run=dry_run,
            backup_dir=args.backup_dir,
            force=args.force,
        )
    except Exception as exc:
        print(f"\n[ERROR] Reconciliation failed: {exc}", file=sys.stderr)
        return 1

    print("\n--- Diagnostic & Parity Summary ---")
    print(f" Total conversation databases on disk: {report.conversations_scanned}")
    print(f" Healthy SQLite databases:             {report.valid_dbs_count}")
    print(f" Corrupted / unreadable databases:     {report.corrupted_dbs_count}")
    print(f" Current indexed summaries in UI:      {report.persisted_summaries_count}")
    print(f" Valid conversations missing from UI:  {len(report.missing_summary_ids)}")
    print(f" Orphan summary entries (no DB):       {len(report.orphan_summary_ids)}")
    print(f" Matching valid IDs:                   {len(report.valid_matching_ids)}")

    if report.missing_summary_ids and args.verbose:
        print("\nMissing Conversation IDs:")
        for mid in report.missing_summary_ids[:10]:
            print(f"  - {mid}")
        if len(report.missing_summary_ids) > 10:
            print(f"  ... and {len(report.missing_summary_ids) - 10} more.")

    if report.orphan_summary_ids and args.verbose:
        print("\nOrphan Summary IDs:")
        for oid in report.orphan_summary_ids[:10]:
            print(f"  - {oid}")
        if len(report.orphan_summary_ids) > 10:
            print(f"  ... and {len(report.orphan_summary_ids) - 10} more.")

    if report.actions_taken:
        print("\nActions Executed:")
        for action in report.actions_taken:
            print(f"  [*] {action}")

    if args.manifest_out:
        dbs = sorted(list(args.conversations_dir.glob("*.db")))
        metas = [inspect_conversation_db(p) for p in dbs]
        export_manifest_csv(metas, args.manifest_out)
        print(f"\n[SUCCESS] Manifest exported to: {args.manifest_out}")

    print("\n" + "=" * 70)
    if report.is_idempotent:
        print(" VERDICT: Stores are in 100% parity. No reconciliation needed.")
    else:
        if dry_run:
            print(" VERDICT: Index drift detected. Run with --apply to reconcile.")
        else:
            print(" VERDICT: Reconciliation complete. All valid sessions restored.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
