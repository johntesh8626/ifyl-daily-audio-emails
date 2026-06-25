from pathlib import Path

from ifyl_daily_audio_emails.kit_broadcast import (
    body_to_html,
    build_broadcast_payload,
    parse_kit_draft_markdown,
)
from ifyl_daily_audio_emails.pipeline import create_draft_from_text


def test_parse_kit_draft_and_build_safe_broadcast_payload(tmp_path: Path):
    result = create_draft_from_text(
        title="Better sleep tonight",
        transcript_text="John Tesh here. Morning light can help your body know when to sleep later tonight.",
        listen_url="https://tesh.com/listen/better-sleep",
        output_dir=tmp_path,
        source_audio="/John Tesh/ifyl-daily-audio-emails/better-sleep.mp3",
    )

    draft = parse_kit_draft_markdown(result.draft_path)
    payload = build_broadcast_payload(draft, holding_tag_id=123)

    assert draft.subject == "Better sleep tonight"
    assert payload["public"] is False
    assert payload["send_at"] is None
    assert payload["subscriber_filter"][0]["all"][0] == {"type": "tag", "ids": [123]}
    assert "utm_source=convertkit" in payload["content"]


def test_body_to_html_preserves_paragraphs_and_links():
    body = "Hi there,\n\nListen now:\nhttps://tesh.com/listen/today\n\nJohn"

    html = body_to_html(body)

    assert "<p>Hi there,</p>" in html
    assert '<a href="https://tesh.com/listen/today">https://tesh.com/listen/today</a>' in html
    assert "<p>John</p>" in html
