from ifyl_daily_audio_emails.dropbox_client import DropboxFile, filter_audio_files, select_candidate


def test_filter_audio_files_uses_include_regex_and_extension():
    files = [
        DropboxFile("1", "today.mp3", "/Intelligence for Your Life emails/today.mp3", "2026-06-25", "a", 1),
        DropboxFile("2", "skip.txt", "/Intelligence for Your Life emails/skip.txt", "2026-06-25", "b", 1),
        DropboxFile("3", "other.mp3", "/Other/other.mp3", "2026-06-25", "c", 1),
    ]

    result = filter_audio_files(files, "Intelligence for Your Life emails")

    assert [file.id for file in result] == ["1"]


def test_select_candidate_prefers_newest_when_no_path():
    files = [
        DropboxFile("old", "old.mp3", "/IFYL emails/old.mp3", "2026-06-24", "a", 1),
        DropboxFile("new", "new.mp3", "/IFYL emails/new.mp3", "2026-06-25", "b", 1),
    ]

    selected = select_candidate(filter_audio_files(files, "IFYL emails"))

    assert selected.id == "new"
