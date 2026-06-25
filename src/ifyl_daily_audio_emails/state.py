from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def processed_key(file_id: str, rev: str) -> str:
    clean_id = str(file_id or "").strip()
    clean_rev = str(rev or "").strip()
    return f"{clean_id}:{clean_rev}" if clean_rev else clean_id


def load_processed_state(path: str | Path) -> dict:
    state_path = Path(path)
    if not state_path.exists():
        return {"processed": {}}
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return {"processed": {}}
    if not isinstance(payload.get("processed"), dict):
        payload["processed"] = {}
    return payload


def is_processed(state: dict, file_id: str, rev: str) -> bool:
    return processed_key(file_id, rev) in state.get("processed", {})


def mark_processed(
    state: dict,
    *,
    file_id: str,
    rev: str,
    path_display: str,
    draft_path: str,
) -> dict:
    processed = state.setdefault("processed", {})
    processed[processed_key(file_id, rev)] = {
        "draft_path": draft_path,
        "path_display": path_display,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "rev": rev,
    }
    return state


def save_processed_state(path: str | Path, state: dict) -> None:
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
