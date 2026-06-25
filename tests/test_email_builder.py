from ifyl_daily_audio_emails.email_builder import (
    add_utm_params,
    build_email_draft,
    subject_from_title,
    title_from_filename,
)


def test_title_from_filename_removes_hour_prefix():
    assert title_from_filename("hr3vt2 morning light helps sleep.mp3") == "Morning light helps sleep"


def test_subject_from_title_is_concise():
    subject = subject_from_title("This is a very long topic title that needs to be shortened for a daily email subject line")

    assert subject.endswith("...")
    assert len(subject) <= 58


def test_add_utm_params_preserves_existing_query():
    url = add_utm_params("https://tesh.com/listen/today?x=1", campaign="daily", content="clip")

    assert "x=1&" in url
    assert "utm_campaign=daily" in url
    assert "utm_content=clip" in url


def test_build_email_draft_preserves_convertkit_personalization():
    draft = build_email_draft(
        title="Better sleep tonight",
        transcript_text="John Tesh here. Morning light can help your body know when to sleep later.",
        listen_url="https://tesh.com/listen/better-sleep",
        source_audio="/Intelligence for Your Life emails/better sleep.mp3",
        target_mode="broadcast",
    )

    assert '{{ subscriber.first_name | default: "there" }}' in draft.body
    assert "John Tesh here." in draft.body
    assert "utm_source=convertkit" in draft.listen_url
    assert 'target_mode: "broadcast"' in draft.markdown
