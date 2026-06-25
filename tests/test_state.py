from pathlib import Path

from ifyl_daily_audio_emails.state import (
    is_processed,
    load_processed_state,
    mark_processed,
    save_processed_state,
)


def test_processed_state_round_trip(tmp_path: Path):
    state_path = tmp_path / "processed.json"
    state = load_processed_state(state_path)

    mark_processed(
        state,
        file_id="id:123",
        rev="abc",
        path_display="/John Tesh/ifyl-daily-audio-emails/today.mp3",
        draft_path="generated/kit-drafts/today.md",
    )
    save_processed_state(state_path, state)

    loaded = load_processed_state(state_path)
    assert is_processed(loaded, "id:123", "abc")
