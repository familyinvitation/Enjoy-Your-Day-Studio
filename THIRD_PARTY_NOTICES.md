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


## The Muser: adapted audio mastering code

src/audio_master.py adapts the two-pass loudness workflow and measurement parser
from src/audio/export.py in https://github.com/noah-chelednik/the-muser,
revision 6eb21f32b66f1c74caf04888f8fb30ecdcdc87ad.
Copyright (c) 2026 The Muser Contributors, MIT license.
The complete license is retained at licenses/the-muser-MIT.txt.
No model weights, voice models, LLM, or demo recordings are included.


## AICoverGen audio effects and mixing adaptation

src/audio_mix.py adapts the effects-chain structure and independent track gains
in src/main.py (add_audio_effects, combine_audio) from
https://github.com/SociallyIneptWeeb/AICoverGen at revision
1babc736e064749c92a481b142bb931b8297c820.
Copyright (c) 2023 SociallyIneptWeeb. MIT license retained in
licenses/AICoverGen-MIT.txt. The implementation uses FFmpeg instead of
Pedalboard/pydub. No RVC models, separation models, recordings, or downloader
are bundled. UltraSinger was reviewed but no source or models were copied.
