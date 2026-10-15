"""Original procedural audio with an animated illustrated scene, rendered by FFmpeg."""
import math
import random
import subprocess
import tempfile
import wave
import hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from .video import centered
from .content import CHANNEL, TAGLINE


def make_audio(kind, job_id, duration, path):
    seed = int(hashlib.sha256(job_id.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    rate = 24000
    with wave.open(str(path), 'wb') as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate)
        previous = 0.0
        for second in range(math.ceil(duration)):
            count = min(rate, int(duration*rate)-second*rate)
            t = np.arange(count)/rate + second
            if kind == 'rain':
                # Filtered noise resembles steady rainfall; not a field recording.
                noise = rng.normal(0, .12, count+1)
                noise[0] = previous
                samples = (noise[1:] + noise[:-1])*.5
                previous = noise[-1]
                samples *= .85 + .1*np.sin(2*np.pi*.12*t)
            else:
                # Slow pentatonic instrumental with smoothly crossfaded chords.
                chords = [(261.63,329.63,392), (220,261.63,329.63),
                          (174.61,220,261.63), (196,246.94,293.66)]
                chord_position = t/8
                blend = .5-.5*np.cos(np.pi*(chord_position % 1))
                current = int(second//8) % 4
                def tone(notes):
                    return sum(np.sin(2*np.pi*f*t + .1*np.sin(.4*t)) for f in notes)/3
                samples = .18*((1-blend)*tone(chords[current])+blend*tone(chords[(current+1)%4]))
            envelope = np.minimum(1, t/2)*np.minimum(1, (duration-t)/2)
            wav.writeframes((np.clip(samples*envelope,-1,1)*32767).astype('<i2').tobytes())
    return path


def scene(kind, label, width=1280, height=720):
    image = Image.new('RGB',(width,height),'#351065')
    d = ImageDraw.Draw(image)
    d.ellipse((width*.70,-height*.35,width*1.15,height*.45),fill='#53248b')
    d.ellipse((width*.76,height*.12,width*.87,height*.31),fill='#ff8952')
    d.polygon([(0,height*.70),(width*.20,height*.40),(width*.43,height*.70),
               (width*.68,height*.37),(width,height*.72),(width,height),(0,height)],fill='#572c91')
    d.polygon([(0,height*.81),(width*.30,height*.60),(width*.60,height*.85),
               (width*.86,height*.58),(width,height*.76),(width,height),(0,height)],fill='#267b89')
    d.rectangle((0,height*.86,width,height),fill='#23b7b0')
    centered(d, CHANNEL, height*.12, int(width*.032),'#fff4d2',width)
    centered(d, label, height*.36, int(width*.057),'#fff4d2',width)
    centered(d, 'RAIN SOUNDS' if kind=='rain' else 'RELAXING MUSIC',height*.52,int(width*.025),'#ff9b70',width)
    centered(d, TAGLINE,height*.93,int(width*.017),'#fff4d2',width)
    return image


def render_ambience(kind,label,job_id,output,duration=60,width=1280,height=720,fps=12):
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        audio = make_audio(kind,job_id,duration,Path(directory)/'audio.wav')
        command=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
                 '-s',f'{width}x{height}','-r',str(fps),'-i','pipe:0','-i',str(audio),
                 '-t',str(duration),'-c:v','libx264','-preset','veryfast','-crf','23',
                 '-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(output)]
        process=subprocess.Popen(command,stdin=subprocess.PIPE)
        seed=int(hashlib.sha256(job_id.encode()).hexdigest()[:8],16)
        rng=random.Random(seed)
        drops=[(rng.random(),rng.random(),rng.uniform(.3,.7)) for _ in range(100)]
        base=scene(kind,label,width,height)
        try:
            for frame in range(math.ceil(duration*fps)):
                t=frame/fps
                image=base.copy();d=ImageDraw.Draw(image)
                if kind=='rain':
                    for x,y,speed in drops:
                        px=x*width;py=((y+t*speed)%1)*height
                        # Leave the title area clear.
                        if height*.32 < py < height*.60:
                            continue
                        d.line((px,py,px-width*.006,py+height*.035),fill='#78d5d6',width=1)
                else:
                    for i in range(24):
                        x=width*(.16+i*.029)
                        h=height*(.015+.045*(1+math.sin(t*.8+i*.45))/2)
                        d.rounded_rectangle((x,height*.77-h,x+width*.009,height*.77+h),radius=3,fill='#69e4d6')
                process.stdin.write(np.asarray(image).tobytes())
            process.stdin.close()
            if process.wait()!=0: raise RuntimeError('Ambience rendering failed')
        except BaseException:
            process.kill();process.wait();raise
    return output
