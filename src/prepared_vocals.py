"""Use a prepared, authorized sung vocal without running a large singing model."""
import subprocess
import tempfile
import wave
from pathlib import Path

from .audio_master import master_wav
from .errors import SafeError


def prepared_vocal(name, output, target_seconds=None, directory=Path('assets/vocals')):
    # An exact filename prevents confusing one person's personalized song with another.
    if not name or any(c in name for c in ('/', '\\', '\0')) or name in ('.', '..'):
        return None
    directory = Path(directory)
    source = next((directory/(name+ext) for ext in ('.wav', '.mp3', '.ogg')
                   if (directory/(name+ext)).is_file()), None)
    if source is None:
        return None
    if not source.resolve().is_relative_to(directory.resolve()):
        raise SafeError('Prepared vocal must be inside assets/vocals.')
    if target_seconds is not None and not 1 <= target_seconds <= 600:
        raise SafeError('Target duration must be 1–600 seconds.')
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as folder:
        decoded = Path(folder)/'vocal.wav'
        subprocess.run(['ffmpeg', '-y', '-nostdin', '-v', 'error', '-i', str(source),
                        '-t', '600', '-ac', '1', '-ar', '22050', '-c:a', 'pcm_s16le',
                        str(decoded)], check=True, capture_output=True, timeout=180)
        master_wav(decoded, -16)
        with wave.open(str(decoded)) as vocal:
            params = vocal.getparams()
            frames = vocal.readframes(params.nframes)
        if params.nframes < params.framerate:
            raise SafeError('Prepared sung vocal must be at least one second long.')
        pause = bytes(params.framerate*params.sampwidth*params.nchannels)
        written = params.nframes
        with wave.open(str(output), 'wb') as result:
            result.setparams(params)
            result.writeframes(frames)
            while target_seconds and written/params.framerate < target_seconds:
                result.writeframes(pause)
                result.writeframes(frames)
                written += params.framerate+params.nframes
    print('Using prepared singing recording; Piper skipped.')
    return output
