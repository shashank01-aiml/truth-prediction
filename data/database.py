"""Owner: Mokireddy Lohith Reddy — SQLite storage for completed tasks (data/timetruth.db)."""
import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).with_name("timetruth.db")
SCHEMA = """CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, difficulty TEXT,
    experience TEXT, priority TEXT, estimate REAL, base_hours REAL, predicted_hours REAL,
    actual_hours REAL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)"""


def _run(sql: str, params: tuple = (), fetch: bool = False):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute(SCHEMA)
        cur = conn.execute(sql, params)
        conn.commit()
        if fetch:
            return [dict(r) for r in cur.fetchall()]
        return cur.lastrowid


def insert_task(rec: dict) -> int:
    cols = ["name", "category", "difficulty", "experience", "priority", "estimate",
            "base_hours", "predicted_hours", "actual_hours"]
    sql = f"INSERT INTO tasks ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})"
    return _run(sql, tuple(rec[c] for c in cols))


def list_tasks() -> list[dict]:
    return _run("SELECT * FROM tasks ORDER BY id DESC", fetch=True)


def delete_task(task_id: int) -> None:
    _run("DELETE FROM tasks WHERE id = ?", (task_id,))


def clear_tasks() -> None:
    _run("DELETE FROM tasks")
