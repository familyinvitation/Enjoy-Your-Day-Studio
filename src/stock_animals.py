"""Real animal footage from Coverr, assembled into a branded compilation."""
from .errors import SafeError
import hashlib
import json
import random
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw
from .config import required
from .video import centered
from .ambience import make_audio

ANIMALS=('cat','dog','rabbit','bird','fish','butterfly','elephant','lion')
ALIASES={'cat':('cat','cats','kitten','kittens'),'dog':('dog','dogs','puppy','puppies'),
         'rabbit':('rabbit','rabbits','bunny','bunnies'),'bird':('bird','birds','parrot','parrots'),
         'fish':('fish','fishes'),'butterfly':('butterfly','butterflies'),
         'elephant':('elephant','elephants'),'lion':('lion','lions')}
PLAY=('playing','play','playful','fetch','toy','toys','chasing','running','hopping','swimming','flying','interacting')

def animal_options(row):
    animal=row[0].strip().lower()
    if animal not in ANIMALS:raise SafeError('Supported animals: '+', '.join(ANIMALS))
    # Old cartoon/pastel rows now select real footage too; no geometric fallback.
    return animal,'real'

def select_clips(videos,animal,job_id):
    chosen=[];seen=set()
    for video in videos:
        # Coverr search can include related subjects: validate species AND activity metadata.
        tags=video.get('tags',[])
        tag_text=' '.join(t if isinstance(t,str) else str(t.get('name','')) for t in tags if isinstance(t,(str,dict)))
        text=' '.join(str(video.get(k,'') or '') for k in ('title','description','slug'))+' '+tag_text
        words=set(re.findall(r'[a-z]+',text.lower()))
        if not words.intersection(ALIASES[animal]) or not words.intersection(PLAY):continue
        identifier=str(video.get('id',''))
        if not identifier or identifier in seen or video.get('is_vertical'):continue
        urls=video.get('urls') or {}
        download=urls.get('mp4_download')
        if not isinstance(download,str) or not download:continue
        if not allowed_media_url(download):continue
        # Do not include AI-generated footage when an explicit flag identifies it.
        if video.get('is_ai_generated') or video.get('generation_type') in ('ai','generated'):continue
        seen.add(identifier)
        page=video.get('url') or video.get('page_url')
        if not isinstance(page,str) or urlparse(page).hostname not in ('coverr.co','www.coverr.co'):
            page='https://coverr.co'
        else:
            parsed=urlparse(page)
            page=parsed._replace(query='',fragment='').geturl()
        chosen.append({'id':identifier,'page':page,'creator':'Coverr', 'download':download})
    random.Random(job_id).shuffle(chosen)
    if len(chosen)<2:
        raise SafeError(f'Coverr search returned {len(videos)} records but only {len(chosen)} usable active-{animal} clips. At least two are required; try another animal or query.')
    return chosen[:8]

def allowed_media_url(url):
    parsed=urlparse(url)
    host=parsed.hostname or ''
    return parsed.scheme=='https' and (host=='coverr.co' or host.endswith('.coverr.co')) and not parsed.username

def coverr_request(query):
    params=urlencode({'query':query,'page':0,'page_size':40,'urls':'true'})
    request=Request('https://api.coverr.co/videos?'+params,
                    headers={'Authorization':'Bearer '+required('COVERR_API_KEY'),'User-Agent':'EnjoyYourDayStudio'})
    with urlopen(request,timeout=60) as response:
        data=json.load(response)
    if not isinstance(data,dict) or not isinstance(data.get('hits'),list):
        raise SafeError('Coverr response format did not contain the expected hits list. The adapter may need an API schema update.')
    return data['hits']

def search_clips(animal,job_id):
    videos=[]
    # At most three search requests per animal job, with no broad unrelated fallback.
    queries=[f'{animal} playing',f'{animal} playful',animal]
    for query in queries:
        hits=coverr_request(query)
        print(f'Coverr search for {animal}: {len(hits)} records on attempt {queries.index(query)+1}.')
        videos.extend(hits)
        try:
            return select_clips(videos,animal,job_id)
        except ValueError:
            continue
    return select_clips(videos,animal,job_id)

def download_clip(url,path):
    if not allowed_media_url(url):
        raise SafeError('Unexpected Coverr download host')
    # Use mp4_download directly, as required by Coverr download tracking.
    # Never pass API authorization to the media CDN or save signed URLs in credits.
    with urlopen(url,timeout=90) as response,path.open('wb') as target:
        total=0
        while True:
            chunk=response.read(1024*1024)
            if not chunk:break
            total+=len(chunk)
            if total>250*1024*1024:raise SafeError('Source clip too large')
            target.write(chunk)

def cached_thumbnail(job_id):
    token=hashlib.sha256(job_id.encode()).hexdigest()
    return Path('.cache/animal-thumbnails')/(token+'.jpg')

def save_thumbnail(animal,video,path):
    frame=path.with_suffix('.frame.jpg')
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(video),'-frames:v','1',str(frame)],check=True)
    with Image.open(frame) as source:image=source.convert('RGB').resize((1280,720))
    draw=ImageDraw.Draw(image)
    draw.rectangle((0,570,1280,720),fill='#351065')
    centered(draw,f'{animal.title()} • Playful Moments',590,60,'#fff4d2',1280)
    centered(draw,'ENJOY YOUR DAY STUDIO',675,24,'#71e3d7',1280)
    image.save(path,'JPEG',quality=90,optimize=True)
    frame.unlink(missing_ok=True)

def real_thumbnail(animal,job_id,path):
    cached=cached_thumbnail(job_id)
    if not cached.exists():
        raise SafeError('Original footage thumbnail is not cached; do not substitute a different animal frame')
    path.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(cached,path)
    return path

def render_animal(animal,visual_style,job_id,output,duration=30):
    clips=search_clips(animal,job_id)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        directory=Path(directory);parts=[]
        for index,clip in enumerate(clips):
            source=directory/f'source-{index}.mp4';part=directory/f'part-{index}.mp4'
            download_clip(clip['download'],source)
            subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(source),'-t','10','-an',
                '-vf','scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24',
                '-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p',str(part)],check=True)
            parts.append(part)
            if index==0:
                thumb=output.with_suffix('.jpg');save_thumbnail(animal,part,thumb)
                cached=cached_thumbnail(job_id);cached.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(thumb,cached)
        listing=directory/'concat.txt'
        listing.write_text(''.join(f"file '{part.name}'\n" for part in parts))
        compilation=directory/'compilation.mp4'
        subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(listing),
                        '-c','copy',str(compilation)],check=True)
        audio=make_audio('music',job_id,duration,directory/'music.wav')
        subprocess.run(['ffmpeg','-y','-loglevel','error','-stream_loop','-1','-i',str(compilation),
            '-i',str(audio),'-map','0:v:0','-map','1:a:0','-t',str(duration),'-c:v','copy','-c:a','aac',
            '-movflags','+faststart',str(output)],check=True)
    # Include credits in upload metadata; API key is never written to a file.
    output.with_suffix('.sources.json').write_text(json.dumps([
        {'creator':clip['creator'],'url':clip['page'],'id':clip['id']} for clip in clips],indent=2))
    return output
