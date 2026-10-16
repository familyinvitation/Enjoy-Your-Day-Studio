# Optional prepared music

The birthday workflow works without an API, downloaded AI model, or GPU.
It now includes an original, locally synthesized melody, chords, and bass.
Music is reduced while the greeting is spoken and returns between phrases.

To use music prepared with OpenMusic or another source, upload ONE recording
named `birthday.wav`, `birthday.mp3`, or `birthday.ogg` in this folder. WAV takes
priority, followed by MP3 and OGG. The recording is automatically looped,
normalized, faded, and mixed below the voice. Use an instrumental recording.
There is no OpenMusic-generated recording bundled with this project.

OpenMusic reference: https://github.com/ivcylc/OpenMusic
Possible description: Cheerful birthday celebration instrumental, warm piano,
gentle bells, acoustic guitar, lively major-key melody, no vocals.

Generating that recording is a separate step; this integration does not call
the public demo or promise free hosted generation. Check the chosen model's
and recording's permissions before use. No OpenMusic source code or model
weights are copied here; its inference code requires separate dependencies.
