# Workflow

## Product Goal

Send daily John Tesh voice emails that train the audience to open, listen, and expect a personal audio touchpoint. This warms the list for a future monthly paid email-audio product.

## Source Folder

Use this Dropbox folder:

```text
/__DROPBOX FOR ASK JOHN TESH/ifyl-daily-audio-emails
```

John can also send a Dropbox shared folder link for one-off previews, but the permanent cloud workflow should use the authenticated Dropbox path above.

The pipeline also still recognizes folder names like `Intelligence for Your Life emails`, `IFYL emails`, or `daily email`.

## Codex Sidebar Cue

Use the sidebar project named `ifyl-daily-audio-emails`. The command phrase is:

```text
Run the IFYL daily audio email drafts.
```

That command means "scan Dropbox for new audio, upload it to R2, and prepare drafts," not "send an email."

## Preview

Open this local file to see the current email wrapper:

```text
previews/ifyl-daily-audio-email-preview.html
```

## Draft Format

Each generated draft contains:

- Subject
- Body copied from the cleaned audio transcription
- Optional `→ Listen here` link to the R2-hosted audio
- ConvertKit-safe markdown
- Source audio path
- Listen URL
- Target metadata: `draft_queue`, `broadcast`, or `sequence`
- Recipient decision: `choose_at_send_time`
- Status: `ready_for_manual_kit_draft`

## Kit Publishing

First release uses manual approval:

1. John asks for a run, or manually starts the GitHub Action.
2. New audio is downloaded from Dropbox and uploaded to Cloudflare R2.
3. The R2 public URL becomes the email listen link.
4. New files are transcribed and wrapped as drafts in `generated/kit-drafts/`.
5. `generated/processed-dropbox-files.json` prevents duplicate drafts on the next run.
6. John chooses which draft to send and which Kit list/destination should receive it.
7. Codex imports into Kit only after John approves that action.

Do not auto-send to the live daily list. The system builds draft inventory only.

## Kit Draft Broadcasts

The Kit step creates broadcast drafts, not an automated sequence:

```bash
python -m ifyl_daily_audio_emails.cli kit-sync-drafts
python -m ifyl_daily_audio_emails.cli kit-sync-drafts --apply
```

Safety defaults:

- `send_at` is null, so the broadcast is not scheduled.
- `public` is false, so the draft is not published as a newsletter web post.
- The default recipient filter is a holding tag named `SYSTEM - IFYL Daily Audio Drafts - Do Not Send`.
- The apply step refuses drafts that still have a missing listen URL.
- John chooses the real list, tag, or segment inside Kit when he is ready to send.

## Audio Hosting

Use the same Cloudflare R2 pattern as the pain/mobility audio:

```text
Dropbox source audio
  -> Wrangler upload to R2 bucket
  -> https://<R2_AUDIO_DOMAIN>/audio/ifyl-daily-audio-emails/<slug>.mp3
  -> Kit draft email listen link
```

Required settings:

- `R2_AUDIO_DOMAIN` or `NEXT_PUBLIC_R2_AUDIO_DOMAIN`
- `R2_AUDIO_PREFIX`, default `audio/ifyl-daily-audio-emails`
- `R2_BUCKET`
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`

## Optional Later Automation

After a few manual runs look right, the GitHub Action can add a cron schedule such as `0 */2 * * *` to check Dropbox every two hours. That should stay disabled during the first validation phase.

## Open Product Decisions

- Should the email link to an audio landing page or direct audio?
- Should weekend emails be skipped?
- Should drafts be reviewed every day or batched weekly before Kit import?
