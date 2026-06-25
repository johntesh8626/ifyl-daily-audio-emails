# IFYL Daily Audio Email Preview

This is the current wrapper shape generated for each Dropbox audio file.

**Subject:** The 30-second reset

**Body:**

Hi {{ subscriber.first_name | default: "there" }},

John Tesh here.

I recorded today's Intelligence for Your Life audio because this idea is worth keeping close: one short pause before you answer a stressful message can change the whole direction of your day.

Take a minute and listen when you have a quiet moment.

Listen to today's audio:
https://audio.example.com/audio/ifyl-daily-audio-emails/the_30_second_reset.mp3

I'll be back tomorrow with another short audio note.

John

## Kit Draft Behavior

- Created as a Kit broadcast draft, not a sequence email.
- `send_at` stays empty/null, so it is not scheduled.
- `public` is false, so it is not published as a web post.
- The default safety audience is the holding tag `SYSTEM - IFYL Daily Audio Drafts - Do Not Send`.
- John chooses the real list/tag/segment when he is ready to send.
- Do not create Kit drafts until the listen URL points to a real R2-hosted audio page or file.
