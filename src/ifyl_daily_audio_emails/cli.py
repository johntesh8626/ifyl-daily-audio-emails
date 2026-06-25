from __future__ import annotations

import argparse
import json

from .config import load_settings
from .pipeline import create_draft_from_text, run_once


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare IFYL daily audio email drafts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    draft = subparsers.add_parser("draft", help="Create a draft from supplied transcript text")
    draft.add_argument("--title", required=True)
    draft.add_argument("--transcript-text", required=True)
    draft.add_argument("--listen-url", default="")
    draft.add_argument("--source-audio", default="")
    draft.add_argument("--target-mode", default="undecided")
    draft.add_argument("--output-dir", default="generated/kit-drafts")
    draft.add_argument("--dry-run", action="store_true")

    run = subparsers.add_parser("run-once", help="Pull one Dropbox audio file and create a Kit-ready draft")
    run.add_argument("--dropbox-path", default=None)
    run.add_argument("--output-dir", default="generated/kit-drafts")
    run.add_argument("--dry-run", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "draft":
        result = create_draft_from_text(
            title=args.title,
            transcript_text=args.transcript_text,
            listen_url=args.listen_url,
            output_dir=args.output_dir,
            source_audio=args.source_audio,
            target_mode=args.target_mode,
            dry_run=args.dry_run,
        )
    else:
        result = run_once(
            settings=load_settings(),
            dropbox_path=args.dropbox_path,
            dry_run=args.dry_run,
            output_dir=args.output_dir,
        )

    print(
        json.dumps(
            {
                "draftPath": result.draft_path.as_posix(),
                "dryRun": result.dry_run,
                "listenUrl": result.listen_url,
                "sourceAudio": result.source_audio,
                "subject": result.subject,
                "title": result.title,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
