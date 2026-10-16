import os
import json
import httplib2
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from .config import required

class YouTube:
    def __init__(self):
        credentials = Credentials(token=None, refresh_token=required('YOUTUBE_REFRESH_TOKEN'),
            client_id=required('YOUTUBE_CLIENT_ID'), client_secret=required('YOUTUBE_CLIENT_SECRET'),
            token_uri='https://oauth2.googleapis.com/token',
            scopes=['https://www.googleapis.com/auth/youtube.upload',
                    'https://www.googleapis.com/auth/youtube.readonly'])
        self.api = build('youtube', 'v3', credentials=credentials, cache_discovery=False)
        channels = self.api.channels().list(part='id', mine=True).execute(num_retries=3).get('items', [])
        if len(channels) != 1 or channels[0]['id'] != required('YOUTUBE_CHANNEL_ID'):
            raise ValueError('OAuth channel does not match YOUTUBE_CHANNEL_ID. Authorize the correct channel.')
    def upload(self, name, job_id, path, content_kind="birthday", visual_style="cartoon"):
        from .content import metadata
        privacy = os.getenv('YOUTUBE_PRIVACY', 'private')
        if privacy not in ('private', 'unlisted', 'public'):
            raise ValueError('Invalid YOUTUBE_PRIVACY')
        made_for_kids = os.getenv('MADE_FOR_KIDS', '')
        if made_for_kids not in ('true', 'false'):
            raise ValueError('Set MADE_FOR_KIDS to true or false based on your actual intended audience.')
        snippet = metadata(content_kind, name, visual_style)
        if content_kind == 'animal':
            sources=path.with_suffix('.sources.json')
            if sources.exists():
                credits=json.loads(sources.read_text())
                snippet['description'] += '\n\nFootage credits (Pexels):\n'+'\n'.join(
                    f"{item['creator']}: {item['url']}" for item in credits)
        snippet['description'] += f'\n\nReference: {job_id}'
        snippet.update(defaultLanguage='en', defaultAudioLanguage='en')
        body = {'snippet': snippet, 'status': {'privacyStatus': privacy,
                'selfDeclaredMadeForKids': made_for_kids == 'true'}}
        request = self.api.videos().insert(part='snippet,status', body=body,
            media_body=MediaFileUpload(str(path), mimetype='video/mp4', chunksize=8*1024*1024, resumable=True))
        response = None
        while response is None:
            # Do not blindly repeat ambiguous failed uploads. The Sheet retains Uploading.
            _, response = request.next_chunk(num_retries=0)
        return response['id']

    def set_thumbnail(self, video_id, path):
        return self.api.thumbnails().set(videoId=video_id,
            media_body=MediaFileUpload(str(path), mimetype='image/jpeg', resumable=False)
        ).execute(num_retries=3)
