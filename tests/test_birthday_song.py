import tempfile
import unittest
import wave
from pathlib import Path
from unittest.mock import patch
from src.birthday_song import personalized_sections, personalized_chorus
from src.content import content_settings
from src.voice import create_voice
from test_voice import FakeVoice

class BirthdaySongTests(unittest.TestCase):
    def test_names_and_repeated_choruses(self):
        words='\n'.join(text for _,text in personalized_sections('Priya'))
        self.assertNotIn('<Name>',words)
        self.assertGreaterEqual(words.count('Happy birthday, Priya'),3)
        self.assertIn('Here’s to Priya',words)
    def test_duration_accepts_birthday_csv(self):
        self.assertEqual(content_settings(['Amit','','','','','','','birthday','120'])[2],120)
        for duration in ('0','59','601'):
            with self.assertRaises(ValueError):content_settings(['Amit','','','','','','','birthday',duration])
    def test_audio_repeats_complete_chorus_until_minimum(self):
        voice=FakeVoice()
        with tempfile.TemporaryDirectory() as directory,patch('src.voice.ensure_voice',return_value=Path('model.onnx')),patch('src.voice.load_voice',return_value=voice):
            output=create_voice('Amit','unused',Path(directory)/'long.wav',target_seconds=3)
            with wave.open(str(output)) as wav:
                seconds=wav.getnframes()/wav.getframerate()
            self.assertGreaterEqual(seconds,3)
            self.assertLess(seconds,4.71)
            self.assertEqual(voice.text,personalized_chorus('Amit'))
