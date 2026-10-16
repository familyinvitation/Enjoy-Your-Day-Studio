import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch
from src.voice import create_voice

class FakeVoice:
    def synthesize_wav(self,text,output):
        self.text=text
        output.setnchannels(1);output.setsampwidth(2);output.setframerate(22050)
        output.writeframes(b'\0\0'*22050)

class VoiceTests(unittest.TestCase):
    def test_personalized_wave_without_google(self):
        voice=FakeVoice()
        with tempfile.TemporaryDirectory() as directory,patch('src.voice.ensure_voice',return_value=Path('model.onnx')),patch('src.voice.load_voice',return_value=voice):
            path=create_voice('Priya','Have an amazing birthday!',Path(directory)/'speech.wav')
            self.assertIn('Happy Birthday Priya!',voice.text)
            with wave.open(str(path)) as wav:self.assertEqual(wav.getnframes(),22050)
    def test_model_error_stops_synthesis(self):
        with patch('src.voice.ensure_voice',side_effect=RuntimeError('download failed')),patch('src.voice.load_voice') as load:
            with self.assertRaises(RuntimeError):create_voice('Amit','Hello',Path('unused.wav'))
            load.assert_not_called()
