import unittest
from unittest.mock import patch
from src import main
from src.stock_animals import animal_options, select_clips, real_thumbnail
from pathlib import Path
from test_queue import FakeSheet

class AnimalTests(unittest.TestCase):
    def test_legacy_style_switches_to_real(self):
        self.assertEqual(animal_options(['Cat','','','','','','','animal','30','neon']),('cat','real'))
    def test_rejects_wrong_species_or_inactive_metadata(self):
        self.assertRaises(ValueError,select_clips,[{'id':1,'url':'https://www.pexels.com/video/dog-playing-1'}],'cat','job')
        self.assertRaises(ValueError,select_clips,[{'id':1,'url':'https://www.pexels.com/video/cat-sleeping-1'}],'cat','job')
    def test_no_substitute_thumbnail(self):
        with patch('src.stock_animals.cached_thumbnail',return_value=Path('/missing/image.jpg')):
            with self.assertRaises(ValueError):real_thumbnail('cat','job',Path('/unused.jpg'))
    def test_animal_pipeline(self):
        queue=FakeSheet([['Cat','Pending','','','job-1','','','animal','30','real']])
        with patch.object(main,'CsvQueue',return_value=queue),patch.object(main,'render_animal') as render,patch.object(main,'create_thumbnail'),patch.object(main,'YouTube') as youtube:
            youtube.return_value.upload.return_value='abc'
            main.run()
            self.assertEqual(render.call_args.args[:2],('cat','real'))
            self.assertEqual(queue.data[0][1],'Uploaded')
