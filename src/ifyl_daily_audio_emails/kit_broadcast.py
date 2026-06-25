from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests


KIT_API_BASE_URL = "https://api.kit.com/v4"
DEFAULT_KIT_BROADCAST_STATE_PATH = "generated/kit-broadcast-drafts.json"
DEFAULT_HOLDING_TAG = "SYSTEM - IFYL Daily Audio Drafts - Do Not Send"
REQUEST_TIMEOUT_SECONDS = 30
PLACEHOLDER_LISTEN_TEXT = "[ADD LISTEN URL]"


@dataclass(frozen=True)
class KitDraftEmail:
    draft_path: Path
    subject: str
    title: str
    body: str
    source_audio: str
    listen_url: str


@dataclass(frozen=True)
class KitBroadcastResult:
    draft_path: Path
    subject: str
    applied: bool
    status: str
    broadcast_id: int | None = None
    holding_tag_id: int | None = None


def discover_draft_paths(draft_dir: str | Path, explicit_paths: Iterable[str] = ()) -> list[Path]:
    paths = [Path(path) for path in explicit_paths if str(path).strip()]
    if paths:
        return sorted(paths)
    return sorted(Path(draft_dir).glob("*.md"))


def parse_kit_draft_markdown(path: str | Path) -> KitDraftEmail:
    draft_path = Path(path)
    text = draft_path.read_text(encoding="utf-8")
    metadata, body_text = parse_markdown_parts(text)
    subject = metadata.get("subject", "").strip()
    if not subject:
        raise ValueError(f"Draft is missing a subject: {draft_path}")
    return KitDraftEmail(
        draft_path=draft_path,
        subject=subject,
        title=metadata.get("title", subject).strip() or subject,
        body=body_text.strip(),
        source_audio=metadata.get("source_audio", "").strip(),
        listen_url=metadata.get("listen_url", "").strip(),
    )


def parse_markdown_parts(text: str) -> tuple[dict[str, str], str]:
    metadata: dict[str, str] = {}
    body_source = text
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            front_matter = text[4:end]
            body_source = text[end + len("\n---") :]
            metadata = parse_front_matter(front_matter)

    marker = "**Body:**"
    body_start = body_source.find(marker)
    if body_start == -1:
        return metadata, body_source.strip()
    return metadata, body_source[body_start + len(marker) :].strip()


def parse_front_matter(front_matter: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for raw_line in front_matter.splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        clean_value = value.strip()
        if clean_value.startswith('"') and clean_value.endswith('"'):
            try:
                clean_value = json.loads(clean_value)
            except json.JSONDecodeError:
                clean_value = clean_value.strip('"')
        metadata[key.strip()] = str(clean_value)
    return metadata


def body_to_html(body: str) -> str:
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", body.strip()) if paragraph.strip()]
    return "\n".join(f"<p>{paragraph_to_html(paragraph)}</p>" for paragraph in paragraphs)


def paragraph_to_html(paragraph: str) -> str:
    lines = [line.strip() for line in paragraph.splitlines()]
    rendered_lines = []
    for line in lines:
        if re.fullmatch(r"https?://\S+", line):
            rendered_lines.append(f'<a href="{html.escape(line, quote=True)}">{html.escape(line)}</a>')
        else:
            rendered_lines.append(html.escape(line))
    return "<br>".join(rendered_lines)


def build_preview_text(body: str, limit: int = 140) -> str:
    text = re.sub(r"\s+", " ", body).strip()
    text = re.sub(r"^Hi \{\{ subscriber\.first_name \| default: \"there\" \}\},\s*", "", text)
    text = re.sub(r"^John Tesh here\.\s*", "", text)
    return text[: limit - 3].rstrip() + "..." if len(text) > limit else text


def build_broadcast_payload(draft: KitDraftEmail, holding_tag_id: int | None = None) -> dict:
    validate_ready_for_kit_apply(draft)
    payload: dict = {
        "content": body_to_html(draft.body),
        "description": f"IFYL daily audio draft: {draft.title}",
        "public": False,
        "published_at": None,
        "send_at": None,
        "thumbnail_alt": None,
        "thumbnail_url": None,
        "preview_text": build_preview_text(draft.body),
        "subject": draft.subject,
    }
    if holding_tag_id is not None:
        payload["subscriber_filter"] = [
            {
                "all": [{"type": "tag", "ids": [holding_tag_id]}],
                "any": None,
                "none": None,
            }
        ]
    return payload


def validate_ready_for_kit_apply(draft: KitDraftEmail) -> None:
    if PLACEHOLDER_LISTEN_TEXT in draft.body:
        raise ValueError(f"Draft still needs a real listen URL before Kit import: {draft.draft_path}")
    if not re.match(r"^https?://", draft.listen_url):
        raise ValueError(f"Draft listen_url must be a real http(s) URL before Kit import: {draft.draft_path}")


def ensure_holding_tag(api_key: str, tag_name: str = DEFAULT_HOLDING_TAG) -> int:
    payload = _request_json(
        "POST",
        "/tags",
        api_key=api_key,
        json_body={"name": tag_name},
    )
    tag = payload.get("tag")
    if not isinstance(tag, dict) or not isinstance(tag.get("id"), int):
        raise RuntimeError("Kit did not return a tag id for the draft holding tag.")
    return int(tag["id"])


def create_kit_broadcast_draft(api_key: str, draft: KitDraftEmail, holding_tag_id: int | None) -> int:
    payload = _request_json(
        "POST",
        "/broadcasts",
        api_key=api_key,
        json_body=build_broadcast_payload(draft, holding_tag_id),
    )
    broadcast = payload.get("broadcast")
    if not isinstance(broadcast, dict) or not isinstance(broadcast.get("id"), int):
        raise RuntimeError("Kit did not return a broadcast id for the created draft.")
    return int(broadcast["id"])


def sync_kit_broadcast_drafts(
    *,
    api_key: str,
    draft_paths: Iterable[Path],
    state_path: str | Path = DEFAULT_KIT_BROADCAST_STATE_PATH,
    holding_tag_name: str = DEFAULT_HOLDING_TAG,
    apply: bool = False,
    force: bool = False,
) -> list[KitBroadcastResult]:
    state = load_kit_broadcast_state(state_path)
    parsed_drafts: dict[str, KitDraftEmail] = {}
    for draft_path in draft_paths:
        key = Path(draft_path).as_posix()
        if key in state["broadcasts"] and not force:
            continue
        draft = parse_kit_draft_markdown(draft_path)
        if apply:
            validate_ready_for_kit_apply(draft)
        parsed_drafts[key] = draft

    holding_tag_id = ensure_holding_tag(api_key, holding_tag_name) if apply and parsed_drafts else None
    results: list[KitBroadcastResult] = []

    for draft_path in draft_paths:
        key = Path(draft_path).as_posix()
        if key in state["broadcasts"] and not force:
            existing = state["broadcasts"][key]
            results.append(
                KitBroadcastResult(
                    draft_path=Path(draft_path),
                    subject=str(existing.get("subject", "")),
                    applied=apply,
                    status="already_created",
                    broadcast_id=int(existing["broadcast_id"]),
                    holding_tag_id=holding_tag_id,
                )
            )
            continue

        draft = parsed_drafts[key]
        if not apply:
            results.append(
                KitBroadcastResult(
                    draft_path=draft.draft_path,
                    subject=draft.subject,
                    applied=False,
                    status="planned",
                )
            )
            continue

        broadcast_id = create_kit_broadcast_draft(api_key, draft, holding_tag_id)
        state["broadcasts"][key] = {
            "broadcast_id": broadcast_id,
            "holding_tag_id": holding_tag_id,
            "subject": draft.subject,
        }
        save_kit_broadcast_state(state_path, state)
        results.append(
            KitBroadcastResult(
                draft_path=draft.draft_path,
                subject=draft.subject,
                applied=True,
                status="created",
                broadcast_id=broadcast_id,
                holding_tag_id=holding_tag_id,
            )
        )

    return results


def load_kit_broadcast_state(path: str | Path) -> dict:
    state_path = Path(path)
    if not state_path.exists():
        return {"broadcasts": {}}
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("broadcasts"), dict):
        return {"broadcasts": {}}
    return payload


def save_kit_broadcast_state(path: str | Path, state: dict) -> None:
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _request_json(method: str, path: str, *, api_key: str, json_body: dict | None = None) -> dict:
    if not api_key.strip():
        raise ValueError("Missing required setting: KIT_API_KEY or CONVERTKIT_API_KEY")
    response = requests.request(
        method,
        f"{KIT_API_BASE_URL}{path}",
        headers={
            "Content-Type": "application/json",
            "X-Kit-Api-Key": api_key,
        },
        json=json_body,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Kit API failed ({response.status_code}): {response.text}")
    return response.json()
