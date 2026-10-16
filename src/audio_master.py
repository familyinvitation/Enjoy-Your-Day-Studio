"""Two-pass loudness processing adapted from The Muser's src/audio/export.py.

Copyright (c) 2026 The Muser Contributors. MIT; see licenses/the-muser-MIT.txt.
Adaptations: safe diagnostics, finite measurements, in-place WAV replacement,
explicit sample format, and category-specific targets.
"""
import json
import math
import subprocess
import tempfile
import wave
from pathlib import Path

from .errors import SafeError


def measure(path, target=-20):
    result = subprocess.run(
        ['ffmpeg', '-hide_banner', '-nostdin', '-i', str(path), '-af',
         f'loudnorm=I={target}:LRA=11:TP=-2:print_format=json', '-f', 'null', '-'],
        capture_output=True, text=True, timeout=1800, check=True)
    start, end = result.stderr.rfind('{'), result.stderr.rfind('}')
    try:
        stats = json.loads(result.stderr[start:end+1])
        values = {key: float(stats[key]) for key in
                  ('input_i', 'input_lra', 'input_tp', 'input_thresh', 'target_offset')}
        if not all(math.isfinite(value) for value in values.values()):
            raise ValueError('Non-finite measurement')
        return values
    except (ValueError, KeyError, TypeError) as exc:
        raise SafeError('Audio is silent or its loudness could not be measured.') from exc


def master_wav(path, target=-20):
    """Normalize a local WAV without replacing it unless processing succeeds."""
    path = Path(path)
    if not -30 <= target <= -14:
        raise SafeError('Audio loudness target must be between -30 and -14 LUFS.')
    stats = measure(path, target)
    with wave.open(str(path), 'rb') as source:
        rate, channels = source.getframerate(), source.getnchannels()
    af = (f'loudnorm=I={target}:LRA=11:TP=-2'
          f":measured_I={stats['input_i']}:measured_LRA={stats['input_lra']}"
          f":measured_TP={stats['input_tp']}:measured_thresh={stats['input_thresh']}"
          f":offset={stats['target_offset']}:linear=true")
    with tempfile.TemporaryDirectory(dir=path.parent) as directory:
        output = Path(directory)/'mastered.wav'
        subprocess.run(['ffmpeg', '-y', '-nostdin', '-v', 'error', '-i', str(path),
                        '-af', af, '-ar', str(rate), '-ac', str(channels),
                        '-c:a', 'pcm_s16le', str(output)],
                       capture_output=True, timeout=1800, check=True)
        with wave.open(str(output), 'rb') as check:
            if check.getnframes() == 0:
                raise SafeError('Audio processing produced an empty track.')
        output.replace(path)
    return path
