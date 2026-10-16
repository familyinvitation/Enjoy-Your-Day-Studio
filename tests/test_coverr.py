import io
import json
import os
import unittest
from unittest.mock import patch
from src.stock_animals import select_clips,coverr_request,search_clips,allowed_media_url

def clip(identifier,title='Cat playing with a toy'):
    return {'id':identifier,'title':title,'description':'A playful cat', 'tags':['cat','playing'],
            'is_vertical':False,'urls':{'mp4_download':f'https://storage.coverr.co/videos/{identifier}/download?token=private'}}

class CoverrTests(unittest.TestCase):
    def test_response_selection_and_dedup(self):
        records=[clip('one'),clip('one'),clip('two')]
        result=select_clips(records,'cat','job')
        self.assertEqual({x['id'] for x in result},{'one','two'})
        self.assertTrue(all(x['creator']=='Coverr' for x in result))
    def test_wrong_subject_and_missing_media_fail_closed(self):
        self.assertRaises(ValueError,select_clips,[clip('one'),{'id':'two','title':'cat playing'}],'cat','job')
        self.assertRaises(ValueError,select_clips,[clip('one'),clip('two')],'dog','job')
    def test_ai_and_vertical_excluded(self):
        a=clip('one');a['is_ai_generated']=True
        b=clip('two');b['is_vertical']=True
        self.assertRaises(ValueError,select_clips,[a,b],'cat','job')
    def test_auth_in_header_only_and_documented_fields(self):
        with patch.dict(os.environ,{'COVERR_API_KEY':'unit-test-secret'}),patch('src.stock_animals.urlopen',return_value=io.BytesIO(json.dumps({'hits':[clip('one')]}).encode())) as opening:
            result=coverr_request('cat playing')
            request=opening.call_args.args[0]
            self.assertNotIn('unit-test-secret',request.full_url)
            self.assertEqual(request.get_header('Authorization'),'Bearer unit-test-secret')
            self.assertIn('urls=true',request.full_url)
            self.assertEqual(result[0]['id'],'one')
    def test_search_call_bound(self):
        with patch('src.stock_animals.coverr_request',return_value=[]) as search:
            with self.assertRaises(ValueError):search_clips('cat','job')
            self.assertEqual(search.call_count,3)
    def test_media_host_validation(self):
        self.assertTrue(allowed_media_url('https://storage.coverr.co/video/test'))
        self.assertFalse(allowed_media_url('https://coverr.co.evil.example/test'))
        self.assertFalse(allowed_media_url('http://storage.coverr.co/test'))
