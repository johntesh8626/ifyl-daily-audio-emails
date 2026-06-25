# AGENTS.md

## Purpose

This repo prepares daily IFYL email drafts from source audio in Dropbox.

Use the same safety posture as the pain/mobility and Deeper Faith workflows:

- Dropbox is the source inbox.
- OpenAI transcription turns audio into text.
- The wrapper is generated into a local/committed draft artifact.
- Kit/ConvertKit publishing requires explicit user approval in the same turn.

## Rules

1. Do not commit secrets, raw downloaded audio, or transient state.
2. Do not auto-send Kit broadcasts or publish Kit sequence emails without explicit user approval.
3. Prefer deterministic scripts for Dropbox scan, download, transcription, and draft generation.
4. Keep generated Kit drafts in `generated/kit-drafts/`.
5. Keep the final email format simple: greeting, short John-style setup, listen link, soft continuity line.
6. Preserve ConvertKit personalization exactly: `{{ subscriber.first_name | default: "there" }}`.
7. If the user asks to import into Kit, use the installed `kit-sequence-importer` skill for sequence UI work unless a direct Kit API path has been explicitly built and verified.
8. Treat broadcast-vs-sequence as a product decision. The code should support both metadata modes, but do not guess which live Kit destination to publish to.

## Local Commands

```bash
pip install -e ".[dev]"
python -m ifyl_daily_audio_emails.cli draft --title "Example" --transcript-text "..." --listen-url "https://example.com"
python -m ifyl_daily_audio_emails.cli run-once --dry-run
pytest
```
