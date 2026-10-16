"""CPU-only adaptation of AICoverGen's effects chain and separate track gains.

Copyright (c) 2023 SociallyIneptWeeb. MIT; licenses/AICoverGen-MIT.txt.
The Pedalboard/pydub implementation is replaced with existing FFmpeg filters.
"""
import json
import math
from pathlib import Path

from .errors import SafeError


def settings(path=Path('assets/audio-settings.json')):
    defaults = {'voice_gain_db': 0, 'music_gain_db': 0, 'vocal_reverb': False}
    if not Path(path).is_file():
        return defaults
    try:
        data = json.loads(Path(path).read_text())
        if not isinstance(data, dict) or set(data)-set(defaults):
            raise ValueError()
        defaults.update(data)
        for key in ('voice_gain_db', 'music_gain_db'):
            value = defaults[key]
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not -12 <= value <= 6:
                raise ValueError()
        if not isinstance(defaults['vocal_reverb'], bool):
            raise ValueError()
    except (ValueError, TypeError):
        raise SafeError('Invalid assets/audio-settings.json: gains must be -12 to +6 dB; vocal_reverb must be true or false.') from None
    return defaults


def birthday_mix():
    options = settings()
    effects = 'highpass=f=75,acompressor=threshold=0.178:ratio=3:attack=15:release=180'
    if options['vocal_reverb']:
        effects += ',aecho=0.8:0.9:45|72:0.08|0.04'
    return (
        f'[1:a]{effects},loudnorm=I=-16:TP=-2:LRA=7,'
        f"volume={options['voice_gain_db']}dB,apad,asplit=2[voice][control];"
        f"[2:a]volume={options['music_gain_db']}dB[music];"
        '[music][control]sidechaincompress=threshold=0.025:ratio=3:attack=30:release=450[bed];'
        '[voice][bed]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95:level=0[a]'
    )
