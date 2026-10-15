import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src import main

class FakeSheet:
    def __init__(self, rows):
        self.data=rows
    def rows(self):
        return [(i,list(row)) for i,row in enumerate(self.data,2)]
    def write(self,i,row):
        self.data[i-2]=list(row)

class QueueTests(unittest.TestCase):
    def exercise(self,status='Pending',failure=False,preview=False):
        sheet=FakeSheet([['Amit',status,'','','job-1','','']])
        with patch.object(main,'credentials'), patch.object(main,'Sheet',return_value=sheet), \
             patch.object(main,'create_voice'),patch.object(main,'render'),patch.object(main,'create_thumbnail'), \
             patch.object(main,'YouTube') as youtube:
            youtube.return_value.upload.return_value='video-123'
            if failure:
                youtube.return_value.upload.side_effect=TimeoutError()
            if failure and status=='Pending' and not preview:
                with self.assertRaises(RuntimeError): main.run(preview)
            else:
                main.run(preview)
            return sheet,youtube.return_value.upload.call_count
    def test_success_is_saved(self):
        sheet,count=self.exercise()
        self.assertEqual(count,1)
        self.assertEqual(sheet.data[0][1],'Uploaded')
        self.assertIn('video-123',sheet.data[0][2])
    def test_uncertain_upload_blocks_retry(self):
        sheet,count=self.exercise(failure=True)
        self.assertEqual(sheet.data[0][1],'Needs Review')
        self.assertEqual(count,1)
        _,count=self.exercise(status='Needs Review')
        self.assertEqual(count,0)
    def test_uploaded_and_inflight_skipped(self):
        for status in ['Uploaded','Uploading','Processing','Error']:
            _,count=self.exercise(status=status)
            self.assertEqual(count,0)
    def test_thumbnail_failure_retries_without_reupload(self):
        sheet=FakeSheet([['Amit','Pending','','','job-1','','']])
        with patch.object(main,'credentials'), patch.object(main,'Sheet',return_value=sheet), \
             patch.object(main,'create_voice'),patch.object(main,'render'),patch.object(main,'create_thumbnail'), \
             patch.object(main,'YouTube') as youtube:
            youtube.return_value.upload.return_value='video-123'
            youtube.return_value.set_thumbnail.side_effect=PermissionError()
            with self.assertRaises(RuntimeError): main.run()
            self.assertEqual(sheet.data[0][1],'Uploaded')
            self.assertTrue(sheet.data[0][6].startswith('Thumbnail pending:'))
            youtube.return_value.set_thumbnail.side_effect=None
            main.run()
            self.assertEqual(youtube.return_value.upload.call_count,1)
            self.assertEqual(youtube.return_value.set_thumbnail.call_count,2)
            self.assertEqual(sheet.data[0][6],'')

    def test_preview_does_not_modify_queue(self):
        sheet,count=self.exercise(preview=True)
        self.assertEqual(count,0)
        self.assertEqual(sheet.data[0][1],'Pending')

if __name__=='__main__': unittest.main()
