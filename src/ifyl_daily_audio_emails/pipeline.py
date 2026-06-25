from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings, require_values
from .dropbox_client import (
    download_file_from_shared_link,
    filter_audio_files,
    list_shared_folder_files,
    refresh_access_token,
    safe_local_audio_path,
    select_candidate,
)
from .email_builder import build_email_draft, slugify, title_from_filename
from .transcribe import transcribe_audio


@dataclass(frozen=True)
class PipelineResult:
    draft_path: Path
    subject: str
    title: str
    source_audio: str
    listen_url: str
    dry_run: bool


def create_draft_from_text(
    *,
    title: str,
    transcript_text: str,
    listen_url: str,
    output_dir: str | Path = "generated/kit-drafts",
    source_audio: str = "",
    target_mode: str = "undecided",
    dry_run: bool = False,
) -> PipelineResult:
    draft = build_email_draft(
        title=title,
        transcript_text=transcript_text,
        listen_url=listen_url,
        source_audio=source_audio,
        target_mode=target_mode,
    )
    filename = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}_{slugify(draft.title)}.md"
    draft_path = Path(output_dir) / filename

    if not dry_run:
        draft_path.parent.mkdir(parents=True, exist_ok=True)
        draft_path.write_text(draft.markdown, encoding="utf-8")

    return PipelineResult(
        draft_path=draft_path,
        subject=draft.subject,
        title=draft.title,
        source_audio=source_audio,
        listen_url=draft.listen_url,
        dry_run=dry_run,
    )


def run_once(
    *,
    settings: Settings,
    dropbox_path: str | None = None,
    dry_run: bool = False,
    output_dir: str | Path = "generated/kit-drafts",
) -> PipelineResult:
    require_values(
        settings,
        [
            "dropbox_app_key",
            "dropbox_app_secret",
            "dropbox_refresh_token",
            "dropbox_shared_link_url",
            "openai_api_key",
        ],
    )
    access_token = refresh_access_token(
        settings.dropbox_app_key,
        settings.dropbox_app_secret,
        settings.dropbox_refresh_token,
    )
    all_files = list_shared_folder_files(access_token, settings.dropbox_shared_link_url)
    eligible_files = filter_audio_files(all_files, settings.dropbox_include_regex)
    candidate = select_candidate(eligible_files, dropbox_path=dropbox_path)
    local_audio_path = safe_local_audio_path(candidate)

    if not dry_run:
        download_file_from_shared_link(
            access_token,
            settings.dropbox_shared_link_url,
            candidate.path_display,
            local_audio_path,
        )

    transcript_text = (
        "[DRY RUN] Transcript would be generated from OpenAI."
        if dry_run
        else transcribe_audio(
            settings.openai_api_key,
            local_audio_path,
            model=settings.openai_transcription_model,
        )
    )
    listen_url = settings.default_listen_url or build_default_listen_url(
        settings.audio_public_base_url,
        candidate.name,
    )

    return create_draft_from_text(
        title=title_from_filename(candidate.name),
        transcript_text=transcript_text,
        listen_url=listen_url,
        output_dir=output_dir,
        source_audio=candidate.path_display,
        target_mode=settings.kit_target_mode,
        dry_run=dry_run,
    )


def build_default_listen_url(audio_public_base_url: str, filename: str) -> str:
    base = audio_public_base_url.strip().rstrip("/")
    if not base:
        return ""
    return f"{base}/{slugify(Path(filename).stem)}"
