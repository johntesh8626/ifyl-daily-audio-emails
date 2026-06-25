from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from .config import Settings, require_values
from .dropbox_client import (
    download_file_by_path,
    download_file_from_shared_link,
    filter_audio_files,
    list_folder_files,
    list_shared_folder_files,
    refresh_access_token,
    safe_local_audio_path,
    select_candidate,
)
from .email_builder import build_email_draft, slugify, title_from_filename
from .state import is_processed, load_processed_state, mark_processed, save_processed_state
from .transcribe import transcribe_audio


DEFAULT_PROCESSED_STATE_PATH = "generated/processed-dropbox-files.json"


@dataclass(frozen=True)
class PipelineResult:
    draft_path: Path
    subject: str
    title: str
    source_audio: str
    source_audio_id: str
    source_audio_rev: str
    listen_url: str
    dry_run: bool


def create_draft_from_text(
    *,
    title: str,
    transcript_text: str,
    listen_url: str,
    output_dir: str | Path = "generated/kit-drafts",
    source_audio: str = "",
    source_audio_id: str = "",
    source_audio_rev: str = "",
    target_mode: str = "draft_queue",
    dry_run: bool = False,
) -> PipelineResult:
    draft = build_email_draft(
        title=title,
        transcript_text=transcript_text,
        listen_url=listen_url,
        source_audio=source_audio,
        target_mode=target_mode,
    )
    filename = f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H%M%SZ')}_{slugify(draft.title)}.md"
    draft_path = Path(output_dir) / filename

    if not dry_run:
        draft_path.parent.mkdir(parents=True, exist_ok=True)
        draft_path.write_text(draft.markdown, encoding="utf-8")

    return PipelineResult(
        draft_path=draft_path,
        subject=draft.subject,
        title=draft.title,
        source_audio=source_audio,
        source_audio_id=source_audio_id,
        source_audio_rev=source_audio_rev,
        listen_url=draft.listen_url,
        dry_run=dry_run,
    )


def run_once(
    *,
    settings: Settings,
    dropbox_path: str | None = None,
    dry_run: bool = False,
    output_dir: str | Path = "generated/kit-drafts",
    state_path: str | Path = DEFAULT_PROCESSED_STATE_PATH,
    force: bool = False,
) -> PipelineResult:
    access_token = prepare_dropbox_access(settings)
    eligible_files = list_eligible_source_files(settings, access_token)
    state = load_processed_state(state_path)

    if dropbox_path:
        candidate = select_candidate(eligible_files, dropbox_path=dropbox_path)
        if is_processed(state, candidate.id, candidate.rev) and not force:
            raise ValueError(f"Dropbox file has already been drafted: {candidate.path_display}")
    else:
        unprocessed = [
            file for file in eligible_files if force or not is_processed(state, file.id, file.rev)
        ]
        candidate = select_candidate(unprocessed)

    result = process_candidate(
        settings=settings,
        access_token=access_token,
        candidate=candidate,
        dry_run=dry_run,
        output_dir=output_dir,
    )
    if not dry_run:
        mark_processed(
            state,
            file_id=candidate.id,
            rev=candidate.rev,
            path_display=candidate.path_display,
            draft_path=result.draft_path.as_posix(),
        )
        save_processed_state(state_path, state)
    return result


def run_pending(
    *,
    settings: Settings,
    dry_run: bool = False,
    output_dir: str | Path = "generated/kit-drafts",
    state_path: str | Path = DEFAULT_PROCESSED_STATE_PATH,
    max_files: int = 10,
    force: bool = False,
) -> list[PipelineResult]:
    access_token = prepare_dropbox_access(settings)
    eligible_files = list_eligible_source_files(settings, access_token)
    state = load_processed_state(state_path)
    candidates = [
        file for file in eligible_files if force or not is_processed(state, file.id, file.rev)
    ][:max(0, max_files)]
    results: list[PipelineResult] = []

    for candidate in candidates:
        result = process_candidate(
            settings=settings,
            access_token=access_token,
            candidate=candidate,
            dry_run=dry_run,
            output_dir=output_dir,
        )
        results.append(result)
        if not dry_run:
            mark_processed(
                state,
                file_id=candidate.id,
                rev=candidate.rev,
                path_display=candidate.path_display,
                draft_path=result.draft_path.as_posix(),
            )
            save_processed_state(state_path, state)

    return results


def prepare_dropbox_access(settings: Settings) -> str:
    require_values(
        settings,
        [
            "dropbox_app_key",
            "dropbox_app_secret",
            "dropbox_refresh_token",
            "openai_api_key",
        ],
    )
    if not settings.dropbox_root_path.strip() and not settings.dropbox_shared_link_url.strip():
        raise ValueError("Missing required settings: dropbox_root_path or dropbox_shared_link_url")
    return refresh_access_token(
        settings.dropbox_app_key,
        settings.dropbox_app_secret,
        settings.dropbox_refresh_token,
    )


def list_eligible_source_files(settings: Settings, access_token: str):
    if settings.dropbox_root_path.strip():
        all_files = list_folder_files(access_token, settings.dropbox_root_path)
    else:
        all_files = list_shared_folder_files(access_token, settings.dropbox_shared_link_url)
    return filter_audio_files(all_files, settings.dropbox_include_regex)


def process_candidate(
    *,
    settings: Settings,
    access_token: str,
    candidate,
    dry_run: bool,
    output_dir: str | Path,
) -> PipelineResult:
    local_audio_path = safe_local_audio_path(candidate)

    if not dry_run:
        if settings.dropbox_root_path.strip():
            download_file_by_path(access_token, candidate.path_display, local_audio_path)
        else:
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
        source_audio_id=candidate.id,
        source_audio_rev=candidate.rev,
        target_mode=settings.kit_target_mode,
        dry_run=dry_run,
    )


def build_default_listen_url(audio_public_base_url: str, filename: str) -> str:
    base = audio_public_base_url.strip().rstrip("/")
    if not base:
        return ""
    return f"{base}/{slugify(Path(filename).stem)}"
