import json
import pytest
from src.reconcile_antigravity_history import (
    reconcile_history,
    StateStoreHandler,
    STATE_TOPIC_KEY,
)

def test_reconciliation_missing_backfill(mock_env):
    conv_dir = mock_env["conv_dir"]
    state_db = mock_env["state_db"]
    create_conv = mock_env["create_conv"]
    seed_summaries = mock_env["seed_summaries"]

    # Create 3 healthy DBs
    c1 = "11111111-1111-1111-1111-111111111111"
    c2 = "22222222-2222-2222-2222-222222222222"
    c3 = "33333333-3333-3333-3333-333333333333"
    create_conv(c1, "Chat 1")
    create_conv(c2, "Chat 2")
    create_conv(c3, "Chat 3")

    # State only has c1, missing c2 and c3
    seed_summaries({
        c1: {"cascadeId": c1, "title": "Chat 1"}
    })

    # Dry run test
    dry_report = reconcile_history(
        conversations_dir=conv_dir,
        state_db_path=state_db,
        dry_run=True,
        force=True,
    )
    assert dry_report.valid_dbs_count == 3
    assert dry_report.persisted_summaries_count == 1
    assert set(dry_report.missing_summary_ids) == {c2, c3}
    assert len(dry_report.orphan_summary_ids) == 0

    # Apply test
    apply_report = reconcile_history(
        conversations_dir=conv_dir,
        state_db_path=state_db,
        dry_run=False,
        force=True,
    )
    assert apply_report.valid_dbs_count == 3
    assert set(apply_report.missing_summary_ids) == {c2, c3}
    assert apply_report.backup_path is not None

    # Verify state.vscdb now has all 3
    handler = StateStoreHandler(state_db)
    raw = handler.read_summaries_raw()[1]
    parsed = json.loads(raw)
    assert set(parsed.keys()) == {c1, c2, c3}


def test_reconciliation_orphan_pruning(mock_env):
    conv_dir = mock_env["conv_dir"]
    state_db = mock_env["state_db"]
    create_conv = mock_env["create_conv"]
    seed_summaries = mock_env["seed_summaries"]

    # Create 1 DB
    c1 = "11111111-1111-1111-1111-111111111111"
    create_conv(c1, "Real chat")

    # State has c1 and a phantom orphan
    phantom = "99999999-9999-9999-9999-999999999999"
    seed_summaries({
        c1: {"cascadeId": c1, "title": "Real chat"},
        phantom: {"cascadeId": phantom, "title": "Phantom orphan"},
    })

    report = reconcile_history(
        conversations_dir=conv_dir,
        state_db_path=state_db,
        dry_run=False,
        prune_orphans=True,
        force=True,
    )
    assert report.orphan_summary_ids == [phantom]

    # Verify phantom is removed
    handler = StateStoreHandler(state_db)
    raw = handler.read_summaries_raw()[1]
    parsed = json.loads(raw)
    assert phantom not in parsed
    assert c1 in parsed
