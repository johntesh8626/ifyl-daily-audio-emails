from pathlib import Path

from ifyl_daily_audio_emails.pipeline import create_draft_from_text


def test_create_draft_from_text_writes_markdown(tmp_path: Path):
    result = create_draft_from_text(
        title="Use one better question",
        transcript_text="John Tesh here. When life feels overwhelming, ask yourself what first step you can take.",
        listen_url="https://tesh.com/listen/question",
        output_dir=tmp_path,
        source_audio="/Intelligence for Your Life emails/question.mp3",
        target_mode="sequence",
    )

    assert result.draft_path.exists()
    text = result.draft_path.read_text(encoding="utf-8")
    assert "**Subject:** Use one better question" in text
    assert "pending_manual_kit_import" in text
    assert "https://tesh.com/listen/question" in text
