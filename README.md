# IFYL Daily Audio Emails

Cloud-ready workflow for turning a short John Tesh audio file into a Kit-ready daily email draft.

The intended path is:

```text
Dropbox audio folder
  -> when John asks for a run, download new eligible audio
  -> transcribe with OpenAI
  -> create the daily IFYL email wrapper
  -> write a Kit-ready markdown draft
  -> John chooses the Kit list/destination when ready to send
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

To preview the current email shape, open:

```text
previews/ifyl-daily-audio-email-preview.html
```

## Codex Sidebar

Open the project named `ifyl-daily-audio-emails`. Say: "Run the IFYL daily audio email drafts." That means scan Dropbox for new files, create draft inventory, and do not send anything.

## Kit Draft Broadcasts

Generated markdown drafts can be turned into Kit broadcast drafts:

```bash
python -m ifyl_daily_audio_emails.cli kit-sync-drafts
python -m ifyl_daily_audio_emails.cli kit-sync-drafts --apply
```

Without `--apply`, the command only previews what would be created. With `--apply`, it creates Kit broadcast drafts using `KIT_API_KEY` or `CONVERTKIT_API_KEY`. Drafts are assigned to the safety tag `SYSTEM - IFYL Daily Audio Drafts - Do Not Send`, remain unscheduled, and are not published as web posts.

## GitHub Actions

Add these repository secrets before running the workflow:

- `DROPBOX_APP_KEY`
- `DROPBOX_APP_SECRET`
- `DROPBOX_REFRESH_TOKEN`
- `OPENAI_API_KEY`

The default Dropbox folder is `/John Tesh/ifyl-daily-audio-emails`. To override it, add a repository variable named `DROPBOX_ROOT_PATH`. A shared-link source is still supported with `DROPBOX_SHARED_LINK_URL`, but the folder you sent is best handled as an authenticated Dropbox path.

The workflow template is in `docs/github-actions/create-daily-email-draft.yml`. Move or copy it into `.github/workflows/` when your GitHub credential has workflow-file permission, then run **Create daily email draft** from the Actions tab.

The recommended first release is manual-on-demand. A two-hour schedule can be added later after the draft style, subject lines, and listen-link destination are proven.

## Current Safety Boundary

This repo writes Kit-ready draft inventory. It does not auto-send or auto-publish Kit emails. John chooses the list, broadcast, or sequence destination when he is ready to send.
