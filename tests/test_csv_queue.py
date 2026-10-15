import base64
import csv
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src.csv_queue import CsvQueue, QueueConflict, HEADERS, OPTIONAL

class CsvQueueTests(unittest.TestCase):
    def text(self):
        out=io.StringIO();csv.writer(out).writerows([HEADERS+OPTIONAL,['Amit','Pending','','','','','','birthday','']]);return out.getvalue()
    def test_local_roundtrip_preserves_type(self):
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'GITHUB_TOKEN':'','GITHUB_ACTIONS':'false'},clear=False):
            path=Path(d)/'queue.csv';path.write_text(self.text())
            with patch.dict(os.environ,{'QUEUE_FILE':str(path)}):
                q=CsvQueue();number,row=q.rows()[0];row[1]='Uploaded';row[2]='https://youtube.com/watch?v=abc'
                q.write(number,row)
                row=CsvQueue().rows()[0][1]
                self.assertEqual(row[1],'Uploaded');self.assertEqual(row[7],'birthday')
    def test_local_conflict_preserves_user_edit(self):
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'GITHUB_TOKEN':'','GITHUB_ACTIONS':'false'},clear=False):
            path=Path(d)/'queue.csv';path.write_text(self.text())
            with patch.dict(os.environ,{'QUEUE_FILE':str(path)}):
                q=CsvQueue();path.write_text('user edits')
                with self.assertRaises(QueueConflict):q.write(*q.rows()[0])
                self.assertEqual(path.read_text(),'user edits')
    def test_persistence_conflict_prevents_upload(self):
        from src import main
        from test_queue import FakeSheet
        queue=FakeSheet([['Amit','Pending','','','job-1','','']])
        with patch.object(main,'CsvQueue',return_value=queue),patch.object(queue,'write',side_effect=QueueConflict()),patch.object(main,'YouTube') as youtube:
            with self.assertRaises(QueueConflict): main.run()
            youtube.return_value.upload.assert_not_called()

    def test_remote_writes_use_updated_sha(self):
        env={'GITHUB_TOKEN':'fake','GITHUB_REPOSITORY':'owner/repo','GITHUB_QUEUE_BRANCH':'main','QUEUE_FILE':'names-template.csv'}
        replies=[{'sha':'first','content':base64.b64encode(self.text().encode()).decode()},
                 {'content':{'sha':'second'}},{'content':{'sha':'third'}}]
        with patch.dict(os.environ,env),patch.object(CsvQueue,'request',side_effect=replies) as request:
            q=CsvQueue();n,row=q.rows()[0];row[1]='Processing';q.write(n,row)
            row[1]='Uploading';q.write(n,row)
            self.assertEqual(request.call_args_list[1].args[1]['sha'],'first')
            self.assertEqual(request.call_args_list[2].args[1]['sha'],'second')
