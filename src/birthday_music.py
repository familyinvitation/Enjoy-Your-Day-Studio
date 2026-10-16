"""Audible birthday accompaniment; optionally use a prepared OpenMusic track."""
import math
import subprocess
import wave
from pathlib import Path

import numpy as np
from .audio_master import master_wav


def prepare_music(output, duration, asset_dir=Path('assets/music')):
    """Loop a supplied recording, or synthesize an original cheerful arrangement."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    source = next((Path(asset_dir)/('birthday'+ext) for ext in ('.wav', '.mp3', '.ogg')
                   if (Path(asset_dir)/('birthday'+ext)).is_file()), None)
    if source:
        subprocess.run([
            'ffmpeg', '-y', '-loglevel', 'error', '-stream_loop', '-1', '-i', str(source),
            '-t', str(duration), '-af',
            f'loudnorm=I=-23:TP=-3:LRA=7,afade=t=in:d=0.5,afade=t=out:st={max(0,duration-1.5)}:d=1.5',
            '-ar', '22050', '-ac', '1', '-c:a', 'pcm_s16le', str(output)
        ], check=True)
        return master_wav(output, target=-23)
    rate = 22050
    audio = np.zeros(int(duration*rate), dtype=np.float64)
    beat = 60/108

    def note(start, length, midi, gain):
        first = int(start*rate)
        last = min(len(audio), first+int(length*rate))
        if first >= last:
            return
        t = np.arange(last-first)/rate
        hz = 440*2**((midi-69)/12)
        envelope = np.minimum(t/.012, 1)*np.exp(-t*3.5/length)
        envelope *= np.minimum((length-t)/.04, 1).clip(0, 1)
        tone = np.sin(2*np.pi*hz*t)+.28*np.sin(4*np.pi*hz*t)+.10*np.sin(6*np.pi*hz*t)
        audio[first:last] += gain*envelope*tone

    # Original C-major melody over C–Am–F–G chords, with bass and bell-like notes.
    chords = [(48,52,55), (45,48,52), (41,45,48), (43,47,50)]
    tune = [72,76,79,76,74,77,79,81,79,76,74,72,74,77,76,72]
    for bar in range(math.ceil(duration/(beat*4))):
        start = bar*beat*4
        chord = chords[bar%4]
        for midi in chord:
            note(start, beat*3.8, midi+12, .045)
        for tick in range(4):
            note(start+tick*beat, beat*.8, chord[0] if tick%2==0 else chord[2], .09)
            note(start+tick*beat, beat*.85, tune[(bar*4+tick)%len(tune)], .13)
            note(start+(tick+.5)*beat, beat*.3, chord[tick%3]+24, .035)
    seconds = np.arange(len(audio))/rate
    audio *= np.minimum(seconds/.5, 1)*np.minimum((duration-seconds)/1.5, 1).clip(0, 1)
    rms = np.sqrt(np.mean(audio**2))
    if rms > 0:
        audio *= min(.07/rms, .8/max(np.max(np.abs(audio)), 1e-9))
    with wave.open(str(output), 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes((audio*32767).astype('<i2').tobytes())
    return master_wav(output, target=-23)
