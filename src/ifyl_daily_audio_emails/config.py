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
    dropbox_shared_link_url: str
    dropbox_include_regex: str
    openai_api_key: str
    openai_transcription_model: str
    audio_public_base_url: str
    default_listen_url: str
    kit_target_mode: str


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
        dropbox_shared_link_url=os.getenv("DROPBOX_SHARED_LINK_URL", ""),
        dropbox_include_regex=os.getenv(
            "DROPBOX_INCLUDE_REGEX",
            str(defaults.get("dropboxIncludeRegex", "")),
        ),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_transcription_model=os.getenv("OPENAI_TRANSCRIPTION_MODEL", "gpt-4o-transcribe"),
        audio_public_base_url=os.getenv("AUDIO_PUBLIC_BASE_URL", ""),
        default_listen_url=os.getenv("DEFAULT_LISTEN_URL", ""),
        kit_target_mode=os.getenv("KIT_TARGET_MODE", str(defaults.get("targetMode", "undecided"))),
    )


def require_values(settings: Settings, fields: list[str]) -> None:
    missing = [field for field in fields if not getattr(settings, field).strip()]
    if missing:
        raise ValueError(f"Missing required settings: {', '.join(missing)}")
