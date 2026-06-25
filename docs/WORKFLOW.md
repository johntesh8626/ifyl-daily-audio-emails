# Workflow

## Product Goal

Send daily John Tesh voice emails that train the audience to open, listen, and expect a personal audio touchpoint. This warms the list for a future monthly paid email-audio product.

## Source Folder

Use a Dropbox folder named something like:

```text
Intelligence for Your Life emails
```

The pipeline can also match `IFYL emails` or `daily email` by default.

## Draft Format

Each generated draft contains:

- Subject
- ConvertKit-safe body
- Source audio path
- Listen URL
- Target metadata: `undecided`, `broadcast`, or `sequence`
- Status: `pending_manual_kit_import`

## Kit Publishing

First release uses manual approval:

1. The GitHub Action or local CLI creates a draft in `generated/kit-drafts/`.
2. Codex reviews the draft with John.
3. John approves the Kit action.
4. Codex imports into Kit using the existing Kit workflow.

Do not auto-send to the live daily list until the broadcast-vs-sequence decision is locked and tested.

## Open Product Decisions

- Broadcast to the existing daily list, evergreen sequence for new subscribers, or both?
- Where should the audio be hosted for the listen link?
- Should the email link to an audio landing page or direct audio?
- Should weekend emails be skipped?
- Should drafts be reviewed every day or batched weekly?
