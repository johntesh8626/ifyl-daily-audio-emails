from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULTS_PATH = ROOT / "config" / "defaults.json"


@dataclass(frozen=True)
class Settings:
    dropbox_app_key: str
    dropbox_app_secret: str
    dropbox_refresh_token: str
    dropbox_root_path: str
    dropbox_shared_link_url: str
    dropbox_include_regex: str
    openai_api_key: str
    openai_transcription_model: str
    audio_public_base_url: str
    default_listen_url: str
    r2_audio_domain: str
    r2_audio_prefix: str
    r2_bucket: str
    wrangler_bin: str
    kit_target_mode: str
    kit_api_key: str
    kit_draft_holding_tag: str


def load_defaults() -> dict:
    if not DEFAULTS_PATH.exists():
        return {}
    return json.loads(DEFAULTS_PATH.read_text(encoding="utf-8"))


def load_dotenv(path: str | Path = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_settings(*, dotenv_path: str | Path = ".env") -> Settings:
    load_dotenv(dotenv_path)
    defaults = load_defaults()

    return Settings(
        dropbox_app_key=os.getenv("DROPBOX_APP_KEY", ""),
        dropbox_app_secret=os.getenv("DROPBOX_APP_SECRET", ""),
        dropbox_refresh_token=os.getenv("DROPBOX_REFRESH_TOKEN", ""),
        dropbox_root_path=os.getenv("DROPBOX_ROOT_PATH", str(defaults.get("dropboxRootPath", ""))),
        dropbox_shared_link_url=os.getenv("DROPBOX_SHARED_LINK_URL", ""),
        dropbox_include_regex=os.getenv(
            "DROPBOX_INCLUDE_REGEX",
            str(defaults.get("dropboxIncludeRegex", "")),
        ),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_transcription_model=os.getenv("OPENAI_TRANSCRIPTION_MODEL", "gpt-4o-transcribe"),
        audio_public_base_url=os.getenv("AUDIO_PUBLIC_BASE_URL", ""),
        default_listen_url=os.getenv("DEFAULT_LISTEN_URL", ""),
        r2_audio_domain=os.getenv(
            "R2_AUDIO_DOMAIN",
            os.getenv("NEXT_PUBLIC_R2_AUDIO_DOMAIN", str(defaults.get("r2AudioDomain", ""))),
        ),
        r2_audio_prefix=os.getenv("R2_AUDIO_PREFIX", str(defaults.get("r2AudioPrefix", ""))),
        r2_bucket=os.getenv("R2_BUCKET", ""),
        wrangler_bin=os.getenv("WRANGLER_BIN", "wrangler"),
        kit_target_mode=os.getenv("KIT_TARGET_MODE", str(defaults.get("targetMode", "draft_queue"))),
        kit_api_key=os.getenv("KIT_API_KEY", os.getenv("CONVERTKIT_API_KEY", "")),
        kit_draft_holding_tag=os.getenv(
            "KIT_DRAFT_HOLDING_TAG",
            str(defaults.get("kitDraftHoldingTag", "SYSTEM - IFYL Daily Audio Drafts - Do Not Send")),
        ),
    )


def require_values(settings: Settings, fields: list[str]) -> None:
    missing = [field for field in fields if not getattr(settings, field).strip()]
    if missing:
        raise ValueError(f"Missing required settings: {', '.join(missing)}")
