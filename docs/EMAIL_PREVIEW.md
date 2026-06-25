# IFYL Daily Audio Email Preview

This is the current wrapper shape generated for each Dropbox audio file.

**Subject:** A quick Intelligence for Your Life audio note

**Body:**

Hi {{ subscriber.first_name | default: "there" }},

John Tesh here.

I recorded today's Intelligence for Your Life audio because this idea is worth keeping close: Morning light can help your body know when to sleep later tonight.

Take a minute and listen when you have a quiet moment:

https://tesh.com/listen/better-sleep?utm_source=convertkit&utm_medium=email&utm_campaign=ifyl_daily_audio&utm_content=better_sleep_tonight

I'll be back tomorrow with another short audio note.

John

## Kit Draft Behavior

- Created as a Kit broadcast draft, not a sequence email.
- `send_at` stays empty/null, so it is not scheduled.
- `public` is false, so it is not published as a web post.
- The default safety audience is the holding tag `SYSTEM - IFYL Daily Audio Drafts - Do Not Send`.
- John chooses the real list/tag/segment when he is ready to send.
