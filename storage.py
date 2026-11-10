"""SQLite persistence for extraction runs and review decisions."""
import json
import sqlite3
from pathlib import Path

DEFAULT_DB = Path(__file__).resolve().parent / "data" / "evidence.sqlite3"

def connect(db_path=DEFAULT_DB):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("""CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        source_url TEXT NOT NULL,
        document TEXT NOT NULL
    )""")
    con.execute("""CREATE TABLE IF NOT EXISTS records (
        run_id INTEGER NOT NULL,
        position INTEGER NOT NULL,
        payload TEXT NOT NULL,
        PRIMARY KEY(run_id, position),
        FOREIGN KEY(run_id) REFERENCES runs(id)
    )""")
    con.commit()
    return con

def save_run(records, document, source_url, db_path=DEFAULT_DB):
    with connect(db_path) as con:
        cur = con.execute("INSERT INTO runs (source_url, document) VALUES (?, ?)", (source_url, document))
        run_id = cur.lastrowid
        con.executemany("INSERT INTO records VALUES (?, ?, ?)", [
            (run_id, i, json.dumps(r, ensure_ascii=False)) for i, r in enumerate(records)
        ])
    return run_id

def latest_run(db_path=DEFAULT_DB):
    with connect(db_path) as con:
        run = con.execute("SELECT id, document, source_url FROM runs ORDER BY id DESC LIMIT 1").fetchone()
        if not run:
            return None
        rows = con.execute("SELECT payload FROM records WHERE run_id = ? ORDER BY position", (run[0],)).fetchall()
    return {"id": run[0], "document": run[1], "source_url": run[2], "records": [json.loads(r[0]) for r in rows]}

def update_record(run_id, position, record, db_path=DEFAULT_DB):
    with connect(db_path) as con:
        cur = con.execute(
            "UPDATE records SET payload = ? WHERE run_id = ? AND position = ?",
            (json.dumps(record, ensure_ascii=False), run_id, position),
        )
        if cur.rowcount != 1:
            raise ValueError("Review record not found in SQLite")
