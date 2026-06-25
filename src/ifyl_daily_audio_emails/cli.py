from __future__ import annotations

import argparse
import json

from .config import load_settings
from .pipeline import DEFAULT_PROCESSED_STATE_PATH, PipelineResult, create_draft_from_text, run_once, run_pending


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare IFYL daily audio email drafts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    draft = subparsers.add_parser("draft", help="Create a draft from supplied transcript text")
    draft.add_argument("--title", required=True)
    draft.add_argument("--transcript-text", required=True)
    draft.add_argument("--listen-url", default="")
    draft.add_argument("--source-audio", default="")
    draft.add_argument("--target-mode", default="draft_queue")
    draft.add_argument("--output-dir", default="generated/kit-drafts")
    draft.add_argument("--dry-run", action="store_true")

    run = subparsers.add_parser("run-once", help="Pull one Dropbox audio file and create a Kit-ready draft")
    run.add_argument("--dropbox-path", default=None)
    run.add_argument("--output-dir", default="generated/kit-drafts")
    run.add_argument("--state-path", default=DEFAULT_PROCESSED_STATE_PATH)
    run.add_argument("--force", action="store_true")
    run.add_argument("--dry-run", action="store_true")

    pending = subparsers.add_parser("run-pending", help="Create drafts for all new eligible Dropbox audio files")
    pending.add_argument("--output-dir", default="generated/kit-drafts")
    pending.add_argument("--state-path", default=DEFAULT_PROCESSED_STATE_PATH)
    pending.add_argument("--max-files", type=int, default=10)
    pending.add_argument("--force", action="store_true")
    pending.add_argument("--dry-run", action="store_true")

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
        print(json.dumps(result_to_json(result), indent=2))
        return 0

    if args.command == "run-once":
        result = run_once(
            settings=load_settings(),
            dropbox_path=args.dropbox_path,
            dry_run=args.dry_run,
            output_dir=args.output_dir,
            state_path=args.state_path,
            force=args.force,
        )
        print(json.dumps(result_to_json(result), indent=2))
        return 0

    results = run_pending(
        settings=load_settings(),
        dry_run=args.dry_run,
        output_dir=args.output_dir,
        state_path=args.state_path,
        max_files=args.max_files,
        force=args.force,
    )
    print(
        json.dumps(
            {
                "draftCount": len(results),
                "drafts": [result_to_json(result) for result in results],
            },
            indent=2,
        )
    )
    return 0


def result_to_json(result: PipelineResult) -> dict:
    return {
        "draftPath": result.draft_path.as_posix(),
        "dryRun": result.dry_run,
        "listenUrl": result.listen_url,
        "sourceAudio": result.source_audio,
        "sourceAudioId": result.source_audio_id,
        "sourceAudioRev": result.source_audio_rev,
        "subject": result.subject,
        "title": result.title,
    }


if __name__ == "__main__":
    raise SystemExit(main())
