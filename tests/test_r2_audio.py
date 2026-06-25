from pathlib import Path

import pytest

from ifyl_daily_audio_emails.r2_audio import (
    build_r2_object_key,
    build_r2_object_url,
    infer_content_type,
    upload_audio_to_r2,
)


def test_build_r2_object_key_uses_daily_audio_prefix():
    assert (
        build_r2_object_key("hr2vt4 Better Sleep Tonight.mp3")
        == "audio/ifyl-daily-audio-emails/hr2vt4_better_sleep_tonight.mp3"
    )


def test_build_r2_object_url_normalizes_domain():
    assert (
        build_r2_object_url(
            "https://audio.example.com/",
            "/audio/ifyl-daily-audio-emails/today.mp3",
        )
        == "https://audio.example.com/audio/ifyl-daily-audio-emails/today.mp3"
    )


def test_infer_content_type_for_audio_formats():
    assert infer_content_type("today.mp3") == "audio/mpeg"
    assert infer_content_type("today.m4a") == "audio/mp4"
    assert infer_content_type("today.wav") == "audio/wav"


def test_upload_audio_to_r2_requires_existing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        upload_audio_to_r2(
            local_audio_path=tmp_path / "missing.mp3",
            r2_bucket="audio-bucket",
            object_key="audio/ifyl-daily-audio-emails/missing.mp3",
        )
