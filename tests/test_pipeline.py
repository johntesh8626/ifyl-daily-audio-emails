from pathlib import Path

from ifyl_daily_audio_emails.config import Settings
from ifyl_daily_audio_emails.pipeline import create_draft_from_text
from ifyl_daily_audio_emails.pipeline import resolve_listen_url


def test_create_draft_from_text_writes_markdown(tmp_path: Path):
    result = create_draft_from_text(
        title="Use one better question",
        transcript_text="John Tesh here. When life feels overwhelming, ask yourself what first step you can take.",
        listen_url="https://audio.example.com/listen/question",
        output_dir=tmp_path,
        source_audio="/Intelligence for Your Life emails/question.mp3",
        target_mode="sequence",
    )

    assert result.draft_path.exists()
    text = result.draft_path.read_text(encoding="utf-8")
    assert "**Subject:** Use one better question" in text
    assert "ready_for_manual_kit_draft" in text
    assert "choose_at_send_time" in text
    assert "https://audio.example.com/listen/question" in text


def test_resolve_listen_url_prefers_r2_public_domain_in_dry_run(tmp_path: Path):
    settings = Settings(
        dropbox_app_key="",
        dropbox_app_secret="",
        dropbox_refresh_token="",
        dropbox_root_path="",
        dropbox_shared_link_url="",
        dropbox_include_regex="",
        openai_api_key="",
        openai_transcription_model="gpt-4o-transcribe",
        audio_public_base_url="",
        default_listen_url="",
        r2_audio_domain="audio.example.com",
        r2_audio_prefix="audio/ifyl-daily-audio-emails",
        r2_bucket="bucket",
        wrangler_bin="wrangler",
        kit_target_mode="draft_queue",
        kit_api_key="",
        kit_draft_holding_tag="tag",
    )

    url = resolve_listen_url(
        settings=settings,
        candidate_name="Better Sleep Tonight.mp3",
        local_audio_path=tmp_path / "missing-ok-in-dry-run.mp3",
        dry_run=True,
    )

    assert url == "https://audio.example.com/audio/ifyl-daily-audio-emails/better_sleep_tonight.mp3"
