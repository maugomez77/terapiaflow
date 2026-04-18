"""TerapiaFlow JSON store."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any

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


def load() -> dict[str, Any]:
    if not STORE_PATH.exists():
        return json.loads(json.dumps(DEFAULT_STATE))
    try:
        data = json.loads(STORE_PATH.read_text())
    except json.JSONDecodeError:
        return json.loads(json.dumps(DEFAULT_STATE))
    for k, v in DEFAULT_STATE.items():
        data.setdefault(k, v)
    return data


def save(state: dict[str, Any]) -> None:
    STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STORE_PATH.write_text(json.dumps(state, indent=2, default=str))


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"
