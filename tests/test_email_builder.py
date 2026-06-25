from ifyl_daily_audio_emails.email_builder import (
    add_utm_params,
    build_email_draft,
    subject_from_title,
    transcript_as_email_body,
    title_from_filename,
)


def test_title_from_filename_removes_hour_prefix():
    assert title_from_filename("hr3vt2 morning light helps sleep.mp3") == "Morning light helps sleep"


def test_subject_from_title_is_concise():
    subject = subject_from_title("This is a very long topic title that needs to be shortened for a daily email subject line")

    assert subject.endswith("...")
    assert len(subject) <= 58


def test_add_utm_params_preserves_existing_query():
    url = add_utm_params("https://audio.example.com/listen/today?x=1", campaign="daily", content="clip")

    assert "x=1&" in url
    assert "utm_campaign=daily" in url
    assert "utm_content=clip" in url


def test_build_email_draft_preserves_convertkit_personalization():
    draft = build_email_draft(
        title="Better sleep tonight",
        transcript_text=(
            "John Tesh here. Morning light can help your body know when to sleep later. "
            "Try getting outside for a few minutes before you check your phone."
        ),
        listen_url="https://audio.example.com/listen/better-sleep",
        source_audio="/Intelligence for Your Life emails/better sleep.mp3",
        target_mode="broadcast",
    )

    assert '{{ subscriber.first_name | default: "there" }}' in draft.body
    assert "John here." in draft.body
    assert "Morning light can help your body know when to sleep later." in draft.body
    assert "Try getting outside for a few minutes before you check your phone." in draft.body
    assert "John Tesh here." not in draft.body
    assert "if you'd rather listen in my voice" in draft.body
    assert "→ Listen here" in draft.body
    assert "utm_source=convertkit" in draft.listen_url
    assert 'target_mode: "broadcast"' in draft.markdown


def test_transcript_as_email_body_uses_full_clean_transcript():
    body = transcript_as_email_body(
        "John here. First thought from the audio. Second thought from the audio. Third thought from the audio. Fourth thought from the audio. Fifth thought from the audio."
    )

    assert body.startswith("First thought")
    assert "Fifth thought from the audio." in body


def test_transcript_as_email_body_removes_john_tesh_with_you_intro():
    body = transcript_as_email_body(
        "John Tesh with you, and I'm here to tell you, going to sleep does not switch off your brain."
    )

    assert body == "Going to sleep does not switch off your brain."
