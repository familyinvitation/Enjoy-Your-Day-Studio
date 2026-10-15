import argparse
import os
import sys
import uuid
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from .config import credentials, validate_name
from .csv_queue import CsvQueue, QueueConflict
from .voice import create_voice
from .content import content_settings
from .ambience import render_ambience
from .animals import animal_options, render_animal
from .video import render, style
from .youtube import YouTube
from .thumbnail import create_thumbnail
from urllib.parse import urlparse, parse_qs

def now():
    return datetime.now(timezone.utc).isoformat()

def finish_thumbnail(sheet, youtube, number, row):
    """Retry only the thumbnail for a durably recorded uploaded video."""
    try:
        kind, name, duration = content_settings(row)
        visual_style = animal_options(row)[1] if kind == 'animal' else 'cartoon'
        video_id = parse_qs(urlparse(row[2]).query).get('v', [''])[0]
        if not video_id or not row[4]:
            raise ValueError('Missing saved video ID or Job ID')
        with tempfile.TemporaryDirectory() as directory:
            thumbnail = create_thumbnail(name, row[4], Path(directory)/'thumbnail.jpg', content_kind=kind, visual_style=visual_style)
            youtube.set_thumbnail(video_id, thumbnail)
        row[6]=''; row[5]=now()
        sheet.write(number, row)
        print(f'Thumbnail applied for row {number}.')
        return True
    except QueueConflict:
        raise
    except Exception as exc:
        row[6]=f'Thumbnail pending: {type(exc).__name__}. Check channel eligibility/permissions. Do not reset video to Pending.'
        row[5]=now()
        sheet.write(number, row)
        print(f'Thumbnail needs attention for row {number} ({type(exc).__name__}).', file=sys.stderr)
        return False


def run(preview=False):
    creds = None
    sheet = CsvQueue()
    rows = sheet.rows()
    youtube = None if preview else YouTube()
    limit = int(os.getenv('MAX_PER_RUN', '3'))
    if not 1 <= limit <= 10:
        raise ValueError('MAX_PER_RUN must be 1–10')
    failures = 0; processed = 0; thumbnail_retries = 0
    for number, row in rows:
        status = row[1].strip().lower()
        if status == 'uploaded' and row[6].startswith('Thumbnail pending:'):
            if not preview and thumbnail_retries < limit:
                thumbnail_retries += 1
                if not finish_thumbnail(sheet, youtube, number, row):
                    failures += 1
            continue
        # Only explicit Pending or blank rows are eligible. Errors require human review.
        if status not in ('', 'pending') or processed >= limit:
            continue
        processed += 1
        uploading = False
        try:
            kind, name, duration = content_settings(row)
            visual_style = animal_options(row)[1] if kind == 'animal' else 'cartoon'
            job_id = row[4] or str(uuid.uuid4())
            if not preview:
                row[4]=job_id; row[1]='Processing'; row[5]=now(); row[6]=''
                sheet.write(number,row)
            with tempfile.TemporaryDirectory() as directory:
                output=Path('output')/f'{job_id}.mp4' if preview else Path(directory)/'video.mp4'
                if kind == 'birthday':
                    if creds is None:
                        creds = credentials()
                    audio=Path(directory)/'voice.wav'
                    _, message=style(job_id)
                    create_voice(name,message,audio,creds)
                    render(name,job_id,audio,output)
                elif kind == 'animal':
                    render_animal(name.lower(),visual_style,job_id,output,duration)
                else:
                    render_ambience(kind,name,job_id,output,duration)
                thumbnail = output.with_suffix('.jpg')
                create_thumbnail(name,job_id,thumbnail,content_kind=kind,visual_style=visual_style)
                if preview:
                    print(f'Preview rendered for row {number}; CSV unchanged.')
                    continue
                row[1]='Uploading'; row[5]=now(); sheet.write(number,row)
                uploading=True
                video_id=youtube.upload(name,job_id,output,content_kind=kind,visual_style=visual_style)
                row[1]='Uploaded'; row[2]=f'https://www.youtube.com/watch?v={video_id}'
                row[3]=now(); row[5]=now(); row[6]='Thumbnail pending: awaiting upload.'
                # If this write fails, preserve Uploading and never automatically upload again.
                sheet.write(number,row)
                uploading=False
                print(f'Uploaded row {number}: {row[2]}')
                if not finish_thumbnail(sheet,youtube,number,row):
                    failures += 1
        except QueueConflict:
            raise
        except Exception as exc:
            failures += 1
            # Do not print raw provider errors which may include credential details.
            print(f'Row {number} failed ({type(exc).__name__}); see CSV recovery instructions.',file=sys.stderr)
            if not preview:
                row[1]='Uploaded' if row[2] else ('Needs Review' if uploading else 'Error')
                row[5]=now(); row[6]=('Thumbnail pending: ' if row[2] else '')+f'{type(exc).__name__}: '+('Check YouTube before retrying; upload may have succeeded.' if uploading else 'Generation or CSV operation failed. Check API setup, billing and permissions.')
                try:
                    sheet.write(number,row)
                except Exception:
                    print('Could not update CSV; existing state remains blocked from automatic retries.',file=sys.stderr)
                    raise
            if uploading:
                break
    if failures:
        raise RuntimeError(f'{failures} row(s) need attention.')

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--preview',action='store_true')
    args=parser.parse_args()
    run(args.preview)
