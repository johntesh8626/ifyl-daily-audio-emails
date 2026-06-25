from __future__ import annotations

from pathlib import Path

import requests


TRANSCRIPTIONS_URL = "https://api.openai.com/v1/audio/transcriptions"
REQUEST_TIMEOUT_SECONDS = 300


def transcribe_audio(api_key: str, audio_file_path: str | Path, *, model: str = "gpt-4o-transcribe") -> str:
    audio_path = Path(audio_file_path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    if not api_key.strip():
        raise ValueError("OPENAI_API_KEY is required to transcribe audio.")

    with audio_path.open("rb") as audio_file:
        response = requests.post(
            TRANSCRIPTIONS_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            data={"model": model, "response_format": "json"},
            files={"file": (audio_path.name, audio_file)},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )

    if response.status_code >= 400:
        raise RuntimeError(f"OpenAI transcription failed ({response.status_code}): {response.text}")

    payload = response.json()
    text = payload.get("text")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError("OpenAI transcription response did not include text.")
    return text.strip()
