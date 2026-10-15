"""Run once locally, never in an Actions runner. Do not commit generated credentials."""
import argparse
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

parser=argparse.ArgumentParser()
parser.add_argument('client_json',type=Path)
args=parser.parse_args()
flow=InstalledAppFlow.from_client_secrets_file(str(args.client_json),
    scopes=['https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.readonly'])
creds=flow.run_local_server(port=0,access_type='offline',prompt='consent')
if not creds.refresh_token:
    raise RuntimeError('No refresh token returned. Revoke prior authorization and try again.')
channels=build('youtube','v3',credentials=creds).channels().list(part='id,snippet',mine=True).execute()['items']
if len(channels)!=1:
    raise RuntimeError('Choose a single YouTube channel during authorization.')
path=Path('youtube-token.json')
path.write_text(json.dumps({'YOUTUBE_CLIENT_ID':creds.client_id,
    'YOUTUBE_CLIENT_SECRET':creds.client_secret,'YOUTUBE_REFRESH_TOKEN':creds.refresh_token,
    'YOUTUBE_CHANNEL_ID':channels[0]['id']},indent=2))
path.chmod(0o600)
print('Authorized channel:',channels[0]['snippet']['title'])
print('Saved youtube-token.json. Copy values into GitHub Secrets; never upload this file.')
