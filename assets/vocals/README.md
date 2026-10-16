# Optional sung birthday vocals

Upload a prepared vocal-only recording named exactly after the CSV name:
`Amit.wav` for `Amit`, or `Priya.mp3` for `Priya`. Names are case-sensitive.
Supported extensions: .wav, .mp3, .ogg, in that priority order.
No example singing recordings are bundled.

The workflow uses the recording instead of Piper, balances its loudness, and
repeats complete recordings with one-second gaps to fill the selected duration.
The existing background music plays underneath. Use a dry vocal-only recording
to avoid mixing two backing tracks. Recordings longer than ten minutes are
limited to the first ten minutes; use a complete short performance instead.
If no matching file exists, the usual Piper spoken greeting is used.
An invalid or silent matching recording stops generation instead of silently
substituting speech. No uploaded video is changed automatically.

SoulX-Singer can be used separately to prepare such a vocal:
https://github.com/Soul-AILab/SoulX-Singer
Its model, reference voice, lyrics, and note preparation are separate steps.
This project does not run its model, call its public demo, or include its code
or weights. Use a voice and recording you have permission to use, and verify
that the audio sings the correct name before adding it here.
