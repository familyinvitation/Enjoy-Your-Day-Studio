# Third-party components

## Piper engine

Maintained upstream: https://github.com/OHF-Voice/piper1-gpl
Installed dependency: piper-tts==1.8.0
License: GPL-3.0 (see upstream LICENSE.md and installed distribution).
Python API: https://github.com/OHF-Voice/piper1-gpl/blob/main/docs/API_PYTHON.md
The engine is installed by pip, not vendored into this ZIP. Preserve its license and meet applicable redistribution requirements if distributing the engine or a derived software package.

## Default female voice

en_US-ljspeech-medium, hosted by rhasspy/piper-voices:
https://huggingface.co/rhasspy/piper-voices/tree/main/en/en_US/ljspeech/medium
Model repository metadata: MIT.
Per-voice model card: https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/ljspeech/medium/MODEL_CARD
The card describes US English female speech and a public-domain training dataset:
https://keithito.com/LJ-Speech-Dataset/
Model, configuration and MODEL_CARD are downloaded together at runtime, not included in this ZIP. Changing voices requires checking the new model's own terms; other Piper voices may use different licenses.

Other dependencies retain their respective upstream licenses. There is no promise of YouTube monetization eligibility or perfect name pronunciation.
