import math
import random
import subprocess
import hashlib
import wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from .audio_mix import birthday_mix

MESSAGES = ['Wishing you joy and a wonderful year ahead!',
            'May your day be filled with smiles and happy memories!',
            'Here is to new adventures and beautiful moments!',
            'Wishing you laughter, love and a fantastic birthday!']
PALETTES = [('#351065', '#fff0cc', '#ff8952'), ('#452076', '#6ce2d6', '#ff9975'),
            ('#512280', '#fff0cc', '#31c7bf'), ('#39115d', '#ffb07e', '#b8a0e6')]

def style(job_id):
    seed = int(hashlib.sha256(job_id.encode()).hexdigest()[:8], 16)
    return seed, MESSAGES[seed % len(MESSAGES)]

def font(size):
    candidates = [Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'),
                  Path('C:/Windows/Fonts/arialbd.ttf')]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    raise ValueError('Install DejaVu Sans fonts or run on GitHub Actions.')

def centered(draw, text, y, size, color, width):
    f = font(size)
    while draw.textbbox((0,0), text, font=f)[2] > width * .88 and size > 12:
        size -= 2
        f = font(size)
    draw.text((width/2, y), text, font=f, fill=color, anchor='mt')

def render(name, job_id, audio, output, width=1080, height=1920, fps=24, duration=None):
    seed, message = style(job_id)
    rng = random.Random(seed)
    bg, accent, secondary = PALETTES[seed % len(PALETTES)]
    if duration is None:
        with wave.open(str(audio)) as wav:
            duration = max(12, wav.getnframes()/wav.getframerate()+2)
    from .birthday_music import prepare_music
    music = output.parent / (output.stem + '-music.wav')
    output.parent.mkdir(parents=True, exist_ok=True)
    prepare_music(music, duration)
    particles = [(rng.random(), rng.random(), rng.uniform(.05,.15), rng.uniform(3,9)) for _ in range(85)]
    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = ['ffmpeg','-y','-loglevel','error','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24',
           '-s',f'{width}x{height}','-r',str(fps),'-i','pipe:0','-i',str(audio),'-i',str(music),
           '-filter_complex',birthday_mix(),
           '-map','0:v:0','-map','[a]','-t',str(duration),'-c:v','libx264',
           '-preset','fast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k',
           '-movflags','+faststart',str(output)]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for frame in range(math.ceil(duration*fps)):
            t = frame/fps
            im = Image.new('RGB', (width,height), bg)
            d = ImageDraw.Draw(im)
            for j,(x,y,speed,size) in enumerate(particles):
                px=x*width; py=((y+t*speed)%1)*height; r=size*width/1080
                d.ellipse((px-r,py-r,px+r,py+r), fill=accent if j%2 else secondary)
            for side in (.12,.88):
                x=width*side; y=height*(.20+.015*math.sin(t*1.3+side))
                rx=width*.075; ry=height*.06
                d.line((x,y+ry,x+width*.02,y+height*.19),fill=accent,width=max(1,width//300))
                d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=secondary)
            centered(d,'HAPPY',height*.28,int(width*.09),accent,width)
            centered(d,'BIRTHDAY',height*.35,int(width*.105),'white',width)
            centered(d,name,height*.47,int(width*(.12+.005*math.sin(t*2))),accent,width)
            # Cake is original procedural artwork, with no external media downloads.
            cx=width/2; cy=height*.68
            d.rounded_rectangle((cx-width*.17,cy,cx+width*.17,cy+height*.08),radius=width*.025,fill=secondary)
            d.rectangle((cx-width*.17,cy,cx+width*.17,cy+height*.016),fill=accent)
            for offset in (-.10,0,.10):
                x=cx+width*offset
                d.rectangle((x-width*.006,cy-height*.038,x+width*.006,cy),fill='white')
                d.ellipse((x-width*.01,cy-height*.052,x+width*.01,cy-height*.038),fill=accent)
            centered(d,'Enjoy your special day!',height*.80,int(width*.043),'white',width)
            centered(d,'ENJOY YOUR DAY STUDIO',height*.90,int(width*.028),accent,width)
            process.stdin.write(np.asarray(im).tobytes())
        process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError('FFmpeg rendering failed')
    except BaseException:
        process.kill(); process.wait()
        raise
    music.unlink(missing_ok=True)
    return output
