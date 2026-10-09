from src.reconcile_antigravity_history import reconcile_history

def test_reconciler_idempotence(mock_env):
    conv_dir = mock_env["conv_dir"]
    state_db = mock_env["state_db"]
    create_conv = mock_env["create_conv"]
    seed_summaries = mock_env["seed_summaries"]

    c1 = "11111111-1111-1111-1111-111111111111"
    c2 = "22222222-2222-2222-2222-222222222222"
    p1 = create_conv(c1, "Chat 1")
    p2 = create_conv(c2, "Chat 2")

    # Start with synchronized state
    seed_summaries({
        c1: {"cascadeId": c1, "title": "Chat 1"},
        c2: {"cascadeId": c2, "title": "Chat 2"},
    })

    mtime_p1_before = p1.stat().st_mtime_ns
    mtime_p2_before = p2.stat().st_mtime_ns
    state_mtime_before = state_db.stat().st_mtime_ns

    # First run (should be no-op)
    report1 = reconcile_history(
        conversations_dir=conv_dir,
        state_db_path=state_db,
        dry_run=False,
        force=True,
    )
    assert report1.is_idempotent is True
    assert len(report1.missing_summary_ids) == 0
    assert len(report1.orphan_summary_ids) == 0
    assert report1.backup_path is None

    # Second run (consecutive check)
    report2 = reconcile_history(
        conversations_dir=conv_dir,
        state_db_path=state_db,
        dry_run=False,
        force=True,
    )
    assert report2.is_idempotent is True
    assert len(report2.actions_taken) == 1
    assert "already synchronized" in report2.actions_taken[0]

    # Verify conversation files were never touched
    assert p1.stat().st_mtime_ns == mtime_p1_before
    assert p2.stat().st_mtime_ns == mtime_p2_before
    assert state_db.stat().st_mtime_ns == state_mtime_before
