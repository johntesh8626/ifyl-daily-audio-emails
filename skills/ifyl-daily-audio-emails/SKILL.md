---
name: ifyl-daily-audio-emails
description: Prepare daily Intelligence for Your Life email drafts from Dropbox audio by running the GitHub-backed IFYL daily audio email pipeline, reviewing the generated Kit-ready draft, and importing it into Kit/ConvertKit only after explicit user approval.
---

# IFYL Daily Audio Emails

Use this skill when John asks to turn daily IFYL Dropbox audio into a Kit/ConvertKit email, create a daily voice email draft, process the `Intelligence for Your Life emails` Dropbox folder, or prepare top-of-funnel daily audio emails.

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
   - Dropbox run: `python -m ifyl_daily_audio_emails.cli run-once`
   - GitHub Action: `Create daily email draft`
3. Review the generated file in `generated/kit-drafts/`.
4. Ask for explicit approval before creating, publishing, or sending anything in Kit.
5. If importing into a Kit sequence, use the existing `kit-sequence-importer` skill.
6. If creating a Kit broadcast, verify the exact recipient segment/tag, subject, body, and send/schedule state with John before making changes.

## Safety

- Never expose or commit Dropbox, OpenAI, or Kit secrets.
- Never auto-send a broadcast.
- Never publish a sequence email unless John has approved that exact operation in the same turn.
- Preserve this personalization exactly: `{{ subscriber.first_name | default: "there" }}`.
