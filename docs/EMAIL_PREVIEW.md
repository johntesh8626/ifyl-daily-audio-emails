# IFYL Daily Audio Email Preview

This is the current wrapper shape generated for each Dropbox audio file.

**Subject:** The 30-second reset

**Body:**

Hi [First Name],

John here.

Before you answer a stressful message, give yourself one short pause. Take one breath, let your shoulders drop, and ask, "What response would I be proud of later?" That small pause can keep the message from setting the tone for the rest of your day.

I recorded a short version of this too - about 90 seconds - if you'd rather listen in my voice.

→ Listen here:
https://audio.example.com/audio/ifyl-daily-audio-emails/the_30_second_reset.mp3

More tomorrow.

John

## Kit Draft Behavior

- Created as a Kit broadcast draft, not a sequence email.
- The readable email body comes from the audio transcript.
- `send_at` stays empty/null, so it is not scheduled.
- `public` is false, so it is not published as a web post.
- The default safety audience is the holding tag `SYSTEM - IFYL Daily Audio Drafts - Do Not Send`.
- John chooses the real list/tag/segment when he is ready to send.
- Do not create Kit drafts until the listen URL points to a real R2-hosted audio page or file.
