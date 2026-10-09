import csv
from pathlib import Path
from src.reconcile_antigravity_history import inspect_conversation_db, export_manifest_csv

def test_inspect_conversation_db(mock_env):
    create_conv = mock_env["create_conv"]
    cascade_id = "c99ca0b3-a658-48ae-9dba-33eed0571a99"
    db_path = create_conv(cascade_id, title="Locate Session Manager Code", step_count=12)

    meta = inspect_conversation_db(db_path)
    assert meta.cascade_id == cascade_id
    assert meta.is_valid_sqlite is True
    assert meta.quick_check_status.lower() == "ok"
    assert meta.step_count == 12
    assert "Locate Session Manager" in meta.title

def test_export_manifest_csv(mock_env):
    create_conv = mock_env["create_conv"]
    db1 = create_conv("11111111-1111-1111-1111-111111111111", title="First chat")
    db2 = create_conv("22222222-2222-2222-2222-222222222222", title="Second chat")

    meta1 = inspect_conversation_db(db1)
    meta2 = inspect_conversation_db(db2)

    csv_out = mock_env["tmp_path"] / "manifest.csv"
    export_manifest_csv([meta1, meta2], csv_out)

    assert csv_out.exists()
    with open(csv_out, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        assert len(reader) == 3  # Header + 2 rows
        assert reader[0][0] == "cascade_id"
        assert reader[1][0] == "11111111-1111-1111-1111-111111111111"
        assert reader[2][0] == "22222222-2222-2222-2222-222222222222"
