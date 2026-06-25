from __future__ import annotations

import mimetypes
import subprocess
from pathlib import Path

from .email_builder import slugify


DEFAULT_R2_AUDIO_PREFIX = "audio/ifyl-daily-audio-emails"


def normalize_domain(value: str) -> str:
    return value.strip().replace("https://", "").replace("http://", "").rstrip("/")


def build_r2_object_key(filename: str, prefix: str = DEFAULT_R2_AUDIO_PREFIX) -> str:
    clean_prefix = prefix.strip().strip("/")
    suffix = Path(filename).suffix.lower() or ".mp3"
    stem = slugify(Path(filename).stem)
    return f"{clean_prefix}/{stem}{suffix}" if clean_prefix else f"{stem}{suffix}"


def build_r2_object_url(domain: str, object_key: str) -> str:
    clean_domain = normalize_domain(domain)
    if not clean_domain:
        return ""
    return f"https://{clean_domain}/{object_key.strip('/')}"


def infer_content_type(path: str | Path) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".mp3":
        return "audio/mpeg"
    if suffix == ".m4a":
        return "audio/mp4"
    if suffix == ".wav":
        return "audio/wav"
    return mimetypes.guess_type(Path(path).name)[0] or "application/octet-stream"


def upload_audio_to_r2(
    *,
    local_audio_path: str | Path,
    r2_bucket: str,
    object_key: str,
    wrangler_bin: str = "wrangler",
) -> None:
    source_path = Path(local_audio_path)
    if not source_path.exists():
        raise FileNotFoundError(f"Audio file not found for R2 upload: {source_path}")
    if not r2_bucket.strip():
        raise ValueError("Missing required setting: R2_BUCKET")

    command = [
        wrangler_bin.strip() or "wrangler",
        "r2",
        "object",
        "put",
        f"{r2_bucket.strip()}/{object_key.strip('/')}",
        "--file",
        source_path.as_posix(),
        "--remote",
        "--content-type",
        infer_content_type(source_path),
    ]
    result = subprocess.run(command, check=False, text=True, capture_output=True)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Wrangler upload failed."
        raise RuntimeError(message)
