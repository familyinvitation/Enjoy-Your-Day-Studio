import shutil
import tempfile
import unittest
import wave
from pathlib import Path

import numpy as np

from src.audio_master import master_wav, measure
from src.errors import SafeError


@unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg required')
class AudioMasterTests(unittest.TestCase):
    def test_quiet_track_reaches_target_without_changing_duration(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'quiet.wav'
            rate = 22050
            t = np.arange(rate*6)/rate
            with wave.open(str(path), 'wb') as out:
                out.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
                out.writeframes((.002*np.sin(2*np.pi*440*t)*32767).astype('<i2').tobytes())
            master_wav(path, -20)
            self.assertAlmostEqual(measure(path, -20)['input_i'], -20, delta=1)
            with wave.open(str(path)) as result:
                self.assertAlmostEqual(result.getnframes()/result.getframerate(), 6, delta=.02)

    def test_silent_track_rejected_without_overwriting(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'silent.wav'
            with wave.open(str(path), 'wb') as out:
                out.setparams((1, 2, 22050, 0, 'NONE', 'not compressed'))
                out.writeframes(bytes(22050*2*4))
            original = path.read_bytes()
            with self.assertRaises(SafeError):
                master_wav(path)
            self.assertEqual(path.read_bytes(), original)
