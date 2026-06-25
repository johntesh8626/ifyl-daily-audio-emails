from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode, urlsplit, urlunsplit


GREETING = 'Hi {{ subscriber.first_name | default: "there" }},'


@dataclass(frozen=True)
class EmailDraft:
    subject: str
    title: str
    body: str
    markdown: str
    listen_url: str


def title_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    stem = re.sub(r"^(hr\d+vt\d+|clip|audio|lesson)[\s_-]+", "", stem, flags=re.IGNORECASE)
    stem = re.sub(r"\s+", " ", stem.replace("_", " ").replace("-", " ")).strip()
    if not stem:
        return "Today's Intelligence for Your Life"
    return stem[:1].upper() + stem[1:]


def subject_from_title(title: str) -> str:
    clean = title.strip().rstrip(".")
    if not clean:
        return "A quick Intelligence for Your Life audio note"
    if len(clean) <= 58:
        return clean[:1].upper() + clean[1:]
    return clean[:55].rstrip() + "..."


def transcript_as_email_body(transcript_text: str) -> str:
    text = strip_host_intro(re.sub(r"\s+", " ", transcript_text).strip())
    if text:
        return text
    return "I wanted to pass along one short Intelligence for Your Life idea today."


def strip_host_intro(text: str) -> str:
    intro_pattern = r"^(?:hi,?\s+)?(?:i'?m\s+)?john(?:\s+tesh)?\s+here\.?\s*"
    while re.match(intro_pattern, text, flags=re.IGNORECASE):
        text = re.sub(intro_pattern, "", text, count=1, flags=re.IGNORECASE)
    return text.strip()


def add_utm_params(url: str, *, campaign: str, content: str = "listen_link") -> str:
    if not url.strip():
        return ""

    parsed = urlsplit(url)
    existing_query = parsed.query
    separator = "&" if existing_query else ""
    tracking = urlencode(
        {
            "utm_source": "convertkit",
            "utm_medium": "email",
            "utm_campaign": campaign,
            "utm_content": content,
        }
    )
    return urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            f"{existing_query}{separator}{tracking}",
            parsed.fragment,
        )
    )


def build_email_draft(
    *,
    title: str,
    transcript_text: str,
    listen_url: str,
    source_audio: str = "",
    target_mode: str = "draft_queue",
) -> EmailDraft:
    normalized_title = title.strip() or "Today's Intelligence for Your Life"
    subject = subject_from_title(normalized_title)
    tracked_url = add_utm_params(
        listen_url.strip(),
        campaign="ifyl_daily_audio",
        content=slugify(normalized_title),
    )
    email_body = transcript_as_email_body(transcript_text)
    listen_target = tracked_url or "[ADD LISTEN URL]"
    body = "\n\n".join(
        [
            GREETING,
            "John here.",
            email_body,
            "I recorded a short version of this too - about 90 seconds - if you'd rather listen in my voice.",
            f"→ Listen here\n{listen_target}",
            "More tomorrow.",
            "John",
        ]
    )
    markdown = render_markdown(
        subject=subject,
        title=normalized_title,
        body=body,
        source_audio=source_audio,
        listen_url=tracked_url or listen_url,
        target_mode=target_mode,
    )
    return EmailDraft(
        subject=subject,
        title=normalized_title,
        body=body,
        markdown=markdown,
        listen_url=tracked_url or listen_url,
    )


def render_markdown(
    *,
    subject: str,
    title: str,
    body: str,
    source_audio: str,
    listen_url: str,
    target_mode: str,
) -> str:
    return "\n".join(
        [
            "---",
            f'subject: "{escape_yaml(subject)}"',
            f'title: "{escape_yaml(title)}"',
            f'source_audio: "{escape_yaml(source_audio)}"',
            f'listen_url: "{escape_yaml(listen_url)}"',
            f'target_mode: "{escape_yaml(target_mode)}"',
            'recipient_decision: "choose_at_send_time"',
            'status: "ready_for_manual_kit_draft"',
            "---",
            "",
            f"**Subject:** {subject}",
            "",
            "**Body:**",
            body,
            "",
        ]
    )


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug[:64] or "daily_audio"


def escape_yaml(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')
