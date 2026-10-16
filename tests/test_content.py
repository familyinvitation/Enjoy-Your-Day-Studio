import unittest
from unittest.mock import patch
from src import main
from src.content import content_settings, metadata
from test_queue import FakeSheet

class ContentTests(unittest.TestCase):
    def test_legacy_birthday(self):
        self.assertEqual(content_settings(['Amit']*1),('birthday','Amit',90))
    def test_invalid_type_and_duration(self):
        for kind,duration in [('unknown','60'),('rain','0'),('music','7201')]:
            with self.assertRaises(ValueError):
                content_settings(['Rain','','','','','','',kind,duration])
    def test_metadata_is_format_specific(self):
        self.assertNotIn('Birthday',metadata('rain','Gentle Rain')['title'])
        self.assertEqual(metadata('music','Calm')['categoryId'],'10')
    def test_ambience_queue_has_no_voice(self):
        for kind in ('rain','music'):
            sheet=FakeSheet([['Gentle Moments','Pending','','','job-1','','',kind,'10']])
            with patch.object(main,'CsvQueue',return_value=sheet), \
                 patch.object(main,'create_voice') as voice,patch.object(main,'render') as birthday, \
                 patch.object(main,'render_ambience') as ambience,patch.object(main,'create_thumbnail'), \
                 patch.object(main,'YouTube') as youtube:
                youtube.return_value.upload.return_value='video-123'
                main.run()
                voice.assert_not_called();birthday.assert_not_called()
                ambience.assert_called_once()
                self.assertEqual(youtube.return_value.upload.call_args.kwargs['content_kind'],kind)
                self.assertEqual(sheet.data[0][1],'Uploaded')
                self.assertEqual(sheet.data[0][7],kind)
