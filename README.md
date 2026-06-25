# IFYL Daily Audio Emails

Cloud-ready workflow for turning a short John Tesh audio file into a Kit-ready daily email draft.

The intended path is:

```text
Dropbox audio folder
  -> download newest eligible audio
  -> transcribe with OpenAI
  -> create the daily IFYL email wrapper
  -> write a Kit-ready markdown draft
  -> Codex imports/publishes in Kit after approval
```

This mirrors the safer pattern used by the existing audio connector and pain/mobility publishing flow: the deterministic code prepares the content, and the final Kit change is verified before it goes live.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
python -m ifyl_daily_audio_emails.cli draft \
  --title "A smarter way to start your day" \
  --transcript-text "John Tesh here. Here is today's Intelligence for Your Life..." \
  --listen-url "https://example.com/listen/today"
```

Generated drafts land in `generated/kit-drafts/`.

## GitHub Actions

Add these repository secrets before running the workflow:

- `DROPBOX_APP_KEY`
- `DROPBOX_APP_SECRET`
- `DROPBOX_REFRESH_TOKEN`
- `DROPBOX_SHARED_LINK_URL`
- `OPENAI_API_KEY`

The workflow template is in `docs/github-actions/create-daily-email-draft.yml`. Move or copy it into `.github/workflows/` when your GitHub credential has workflow-file permission, then run **Create daily email draft** from the Actions tab.

## Current Safety Boundary

This repo writes Kit-ready drafts. It does not auto-send or auto-publish Kit emails yet. That keeps the top-of-funnel daily list safe while we finalize whether the target should be broadcasts, an evergreen sequence, or both.
