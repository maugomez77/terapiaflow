"""Persistence for TerapiaFlow.

Uses Neon/PostgreSQL when DATABASE_URL is set (production, Render).
Falls back to a local JSON file when not set (dev).
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

PROJECT = "terapiaflow"

STORE_PATH = Path(os.environ.get("TERAPIAFLOW_STORE",
                                   Path.home() / ".terapiaflow" / "store.json"))

DEFAULT_STATE: dict[str, Any] = {
    "patients": [],
    "episodes": [],
    "sessions": [],
    "home_exercises": [],
    "claims": [],
    "compliance_checks": [],
}


def _db_url() -> str | None:
    return os.environ.get("DATABASE_URL")


def _pg_connect():
    import psycopg
    return psycopg.connect(_db_url(), autocommit=True)


def _pg_init(conn) -> None:
    conn.execute(
        "CREATE TABLE IF NOT EXISTS council_stores ("
        "project text PRIMARY KEY, data jsonb NOT NULL)"
    )


def _pg_load() -> dict[str, Any]:
    with _pg_connect() as conn:
        _pg_init(conn)
        cur = conn.execute("SELECT data FROM council_stores WHERE project = %s", (PROJECT,))
        row = cur.fetchone()
    if not row:
        return json.loads(json.dumps(DEFAULT_STATE))
    data = row[0]
    if isinstance(data, str):
        data = json.loads(data)
    for k, v in DEFAULT_STATE.items():
        data.setdefault(k, v)
    return data


def _pg_save(state: dict[str, Any]) -> None:
    with _pg_connect() as conn:
        _pg_init(conn)
        conn.execute(
            "INSERT INTO council_stores (project, data) VALUES (%s, %s::jsonb) "
            "ON CONFLICT (project) DO UPDATE SET data = EXCLUDED.data",
            (PROJECT, json.dumps(state, default=str)),
        )


def _file_load() -> dict[str, Any]:
    if not STORE_PATH.exists():
        return json.loads(json.dumps(DEFAULT_STATE))
    try:
        data = json.loads(STORE_PATH.read_text())
    except json.JSONDecodeError:
        return json.loads(json.dumps(DEFAULT_STATE))
    for k, v in DEFAULT_STATE.items():
        data.setdefault(k, v)
    return data


def _file_save(state: dict[str, Any]) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(state, indent=2, default=str))


def load() -> dict[str, Any]:
    return _pg_load() if _db_url() else _file_load()


def save(state: dict[str, Any]) -> None:
    if _db_url():
        _pg_save(state)
    else:
        _file_save(state)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"
