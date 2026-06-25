---
name: ifyl-daily-audio-emails
description: Prepare daily Intelligence for Your Life email drafts from Dropbox audio by running the GitHub-backed IFYL daily audio email pipeline, reviewing the generated Kit-ready draft, and importing it into Kit/ConvertKit only after explicit user approval.
---

# IFYL Daily Audio Emails

Use this skill when John asks to turn daily IFYL Dropbox audio into a Kit/ConvertKit email, create a daily voice email draft, process the `ifyl-daily-audio-emails` Dropbox folder, or prepare top-of-funnel daily audio emails.

## Repo

Primary repo:

```text
/Users/johntesh16/Documents/Documents - John's macbook 16  2025 water/AUTO LESSON GENERATOR /ifyl-daily-audio-emails
```

GitHub:

```text
https://github.com/johntesh8626/ifyl-daily-audio-emails
```

## Workflow

1. Read `AGENTS.md` and `docs/WORKFLOW.md`.
2. Run or inspect the draft pipeline:
   - Local text test: `python -m ifyl_daily_audio_emails.cli draft ...`
   - Dropbox run for all new files: `python -m ifyl_daily_audio_emails.cli run-pending`
   - Exact Dropbox file run: `python -m ifyl_daily_audio_emails.cli run-once --dropbox-path <path>`
   - GitHub Action: `Create daily email draft`
3. Confirm the audio was uploaded to Cloudflare R2 and the draft listen URL is an R2 public URL, not Dropbox.
4. Review the generated file in `generated/kit-drafts/`.
5. Preview Kit draft broadcast creation with `python -m ifyl_daily_audio_emails.cli kit-sync-drafts`.
6. Ask for explicit approval before running `python -m ifyl_daily_audio_emails.cli kit-sync-drafts --apply`.
7. If importing into a Kit sequence, use the existing `kit-sequence-importer` skill.
8. If creating a Kit broadcast directly in the browser, verify the exact recipient segment/tag, subject, body, and send/schedule state with John before making changes.

## Safety

- Never expose or commit Dropbox, OpenAI, or Kit secrets.
- Never auto-send a broadcast.
- Treat generated drafts as `draft_queue` inventory; John chooses the Kit list or destination at send time.
- Kit API-created drafts should use the holding tag `SYSTEM - IFYL Daily Audio Drafts - Do Not Send`.
- Public listen links should be Cloudflare R2 URLs.
- Never publish a sequence email unless John has approved that exact operation in the same turn.
- Preserve this personalization exactly: `{{ subscriber.first_name | default: "there" }}`.
