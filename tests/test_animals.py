import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src import main
from src.animals import animal_options, animal_frame, ANIMALS, STYLES
from src.thumbnail import create_thumbnail
from test_queue import FakeSheet

class AnimalTests(unittest.TestCase):
    def test_supported_species_and_styles(self):
        for animal in ANIMALS:
            for style in STYLES:
                self.assertEqual(animal_options([animal,'','','','','','','animal','30',style]),(animal,style))
                self.assertEqual(animal_frame(animal,style,width=320,height=180).size,(320,180))
    def test_reject_invalid_options(self):
        for animal,style in [('dragon','cartoon'),('cat','realistic')]:
            with self.assertRaises(ValueError):animal_options([animal,'','','','','','','animal','30',style])
    def test_thumbnail_is_animal_scene(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'cat.jpg'
            create_thumbnail('cat','job',path,content_kind='animal',visual_style='neon')
            self.assertGreater(path.stat().st_size,1000)
    def test_animal_queue_without_voice(self):
        queue=FakeSheet([['Cat','Pending','','','job-1','','','animal','30','neon']])
        with patch.object(main,'CsvQueue',return_value=queue),\
             patch.object(main,'render_animal') as render,patch.object(main,'create_thumbnail') as thumbnail, \
             patch.object(main,'YouTube') as youtube:
            youtube.return_value.upload.return_value='abc'
            main.run()
            render.assert_called_once()
            self.assertEqual(render.call_args.args[:2],('cat','neon'))
            self.assertEqual(youtube.return_value.upload.call_args.kwargs['content_kind'],'animal')
            self.assertEqual(youtube.return_value.upload.call_args.kwargs['visual_style'],'neon')
            self.assertEqual(queue.data[0][1],'Uploaded')
            self.assertEqual(queue.data[0][9],'neon')
