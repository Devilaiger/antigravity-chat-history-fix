import json
import sqlite3
import pytest
from pathlib import Path

STATE_TOPIC_KEY = "antigravityUnifiedStateSync.trajectorySummaries"

@pytest.fixture
def mock_env(tmp_path: Path):
    """Creates a temporary test environment with conversation databases and a state.vscdb."""
    conv_dir = tmp_path / "conversations"
    conv_dir.mkdir(parents=True)

    state_dir = tmp_path / "globalStorage"
    state_dir.mkdir(parents=True)
    state_db = state_dir / "state.vscdb"

    # Initialize state.vscdb schema
    conn = sqlite3.connect(str(state_db))
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE ItemTable (
            key TEXT PRIMARY KEY,
            value TEXT
        );
    """)
    conn.commit()
    conn.close()

    def create_mock_conversation(cascade_id: str, title: str = "Test prompt", step_count: int = 5):
        db_path = conv_dir / f"{cascade_id}.db"
        c = sqlite3.connect(str(db_path))
        cur = c.cursor()
        cur.execute("""
            CREATE TABLE trajectory_meta (
                trajectory_id TEXT,
                cascade_id TEXT,
                trajectory_type INTEGER,
                source INTEGER
            );
        """)
        cur.execute(
            "INSERT INTO trajectory_meta VALUES (?, ?, 4, 1);",
            (f"traj-{cascade_id}", cascade_id),
        )
        cur.execute("""
            CREATE TABLE steps (
                idx INTEGER PRIMARY KEY,
                step_type INTEGER,
                status INTEGER,
                has_subtrajectory NUMERIC,
                step_payload BLOB
            );
        """)
        for i in range(step_count):
            payload = title.encode("utf-8") if i == 0 else b"step data"
            cur.execute(
                "INSERT INTO steps VALUES (?, 1, 1, 0, ?);",
                (i, payload),
            )
        c.commit()
        c.close()
        return db_path

    def seed_state_summaries(summary_dict: dict):
        conn = sqlite3.connect(str(state_db))
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO ItemTable (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value;
            """,
            (STATE_TOPIC_KEY, json.dumps(summary_dict)),
        )
        conn.commit()
        conn.close()

    return {
        "conv_dir": conv_dir,
        "state_db": state_db,
        "tmp_path": tmp_path,
        "create_conv": create_mock_conversation,
        "seed_summaries": seed_state_summaries,
    }
