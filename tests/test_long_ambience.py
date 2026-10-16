import unittest
from src.content import content_settings

class LongAmbienceTests(unittest.TestCase):
    def test_minimum_and_legacy_rows(self):
        for kind in ('rain','music'):
            for duration in ('','60','1799','1800'):
                self.assertEqual(content_settings(['Calm','','','','','','',kind,duration])[2],1800)
            self.assertEqual(content_settings(['Calm','','','','','','',kind,'3600'])[2],3600)
    def test_invalid_durations(self):
        for kind in ('rain','music'):
            for duration in ('0','-1','7201','invalid'):
                with self.assertRaises(ValueError):content_settings(['Calm','','','','','','',kind,duration])
