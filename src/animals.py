"""Animated original illustrated animals: no stock footage or paid video service."""
import math
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
from .video import centered
from .ambience import make_audio

ANIMALS = ('cat','dog','rabbit','bird','fish','butterfly','elephant','lion')
STYLES = ('cartoon','pastel','silhouette','neon')
PALETTES = {
    'cartoon': ('#351065','#ffad7b','#fff4d2','#31c7bf'),
    'pastel': ('#f2e6fa','#b6a1dc','#503c71','#a3d9cc'),
    'silhouette': ('#ffbc96','#30244d','#30244d','#d385a8'),
    'neon': ('#100d2d','#40e3d2','#f2efff','#bd64f9'),
}

def animal_options(row):
    cells=list(row)+['']*10
    animal=cells[0].strip().lower()
    if animal not in ANIMALS:
        raise ValueError('Supported animals: '+', '.join(ANIMALS))
    style=cells[9].strip().lower() or 'cartoon'
    if style not in STYLES:
        raise ValueError('Animal styles: '+', '.join(STYLES))
    return animal, style


def animal_frame(animal, visual_style='cartoon', t=0, width=1280, height=720):
    bg, fur, ink, accent=PALETTES[visual_style]
    image=Image.new('RGB',(1280,720),bg)
    d=ImageDraw.Draw(image)
    # Whole character bobs and moves; wings/tails animate independently.
    cx=640+35*math.sin(t*.8); cy=390+12*math.sin(t*2)
    def box(x1,y1,x2,y2):return (cx+x1,cy+y1,cx+x2,cy+y2)
    def ellipse(x1,y1,x2,y2,color=fur):d.ellipse(box(x1,y1,x2,y2),fill=color)
    def polygon(points,color=fur):d.polygon([(cx+x,cy+y) for x,y in points],fill=color)
    def line(points,color=ink,weight=5):d.line([(cx+x,cy+y) for x,y in points],fill=color,width=weight)
    d.ellipse((370,570,910,615),fill=accent)
    if animal in ('cat','dog','rabbit','lion'):
        if animal=='lion':
            for i in range(12):
                a=i*math.tau/12
                x=math.cos(a)*108;y=-35+math.sin(a)*108
                ellipse(x-45,y-45,x+45,y+45,accent)
        ellipse(-88,40,88,180)
        ellipse(-110,-140,110,80)
        ellipse(-100,135,-15,190);ellipse(15,135,100,190)
        if animal=='cat':
            polygon([(-103,-75),(-110,-190),(-20,-130)])
            polygon([(103,-75),(110,-190),(20,-130)])
            line([(73,112),(150,105+25*math.sin(t*2)),(175,60+25*math.sin(t*2))],fur,23)
            for side in (-1,1):
                for y in (0,20):line([(side*65,y),(side*145,y-10)],ink,4)
        elif animal=='dog':
            ellipse(-155,-145,-85,25,accent);ellipse(85,-145,155,25,accent)
            line([(75,130),(145,65+30*math.sin(t*4))],fur,24)
        elif animal=='rabbit':
            ellipse(-85,-300,-20,-90);ellipse(20,-300,85,-90)
            ellipse(-68,-273,-37,-130,accent);ellipse(37,-273,68,-130,accent)
            ellipse(70,110,128,166,'#fff4e7')
        else:
            ellipse(-120,-150,-60,-90);ellipse(60,-150,120,-90)
        if visual_style!='silhouette':
            # Blink briefly every four seconds.
            if t%4>3.75:
                line([(-62,-49),(-28,-49)]);line([(28,-49),(62,-49)])
            else:
                ellipse(-57,-65,-33,-34,ink);ellipse(33,-65,57,-34,ink)
            ellipse(-34,-8,34,35,'#fff4d2')
            polygon([(-13,0),(13,0),(0,14)],ink)
            line([(0,14),(0,30),(-20,39)]);line([(0,30),(20,39)])
    elif animal=='elephant':
        ellipse(-150,-60,150,150)
        ellipse(-170,-165,-40,20,accent);ellipse(40,-165,170,20,accent)
        ellipse(-100,-170,100,50)
        d.rounded_rectangle(box(-38,-10,38,160+10*math.sin(t*2)),radius=35,fill=fur)
        for x in (-110,55):d.rounded_rectangle(box(x,90,x+55,195),radius=18,fill=fur)
        if visual_style!='silhouette':
            ellipse(-66,-89,-45,-65,ink);ellipse(45,-89,66,-65,ink)
    elif animal=='bird':
        ellipse(-100,-130,100,130)
        flap=40*math.sin(t*4)
        polygon([(-60,-20),(-210,-40-flap),(-120,100)],accent)
        polygon([(60,-20),(210,-40-flap),(120,100)],accent)
        polygon([(80,-75),(145,-45),(85,-20)],accent)
        line([(-40,120),(-40,180),(-68,180)],accent,10)
        line([(40,120),(40,180),(68,180)],accent,10)
        if visual_style!='silhouette':ellipse(30,-85,52,-58,ink)
    elif animal=='fish':
        ellipse(-160,-90,140,95)
        wag=20*math.sin(t*4)
        polygon([(-125,0),(-240,-110+wag),(-240,110+wag)],accent)
        polygon([(-30,-60),(35,-140),(65,-60)],accent)
        if visual_style!='silhouette':
            ellipse(65,-40,94,-10,ink)
            d.arc(box(64,10,120,55),0,110,fill=ink,width=5)
        for i in range(4):
            y=140-((t*50+i*65)%300)
            d.ellipse(box(200,y,220,y+20),outline=accent,width=3)
    else:
        flap=20*math.sin(t*4)
        for side in (-1,1):
            x=side*(95+flap)
            ellipse(x-90,-180,x+90,0,accent)
            ellipse(x-70,-5,x+70,125,fur)
        ellipse(-22,-125,22,130,ink)
        line([(-10,-100),(-50,-175)],ink,5)
        line([(10,-100),(50,-175)],ink,5)
    centered(d,'ENJOY YOUR DAY STUDIO',36,32,ink if visual_style=='pastel' else '#fff4d2',1280)
    centered(d,f'{animal.title()} • {visual_style.title()} Animation',650,38,ink if visual_style=='pastel' else '#fff4d2',1280)
    if (width,height)!=(1280,720):image=image.resize((width,height),Image.Resampling.LANCZOS)
    return image


def render_animal(animal,visual_style,job_id,output,duration=30,width=1280,height=720,fps=12):
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        audio=make_audio('music',job_id,duration,Path(directory)/'music.wav')
        cmd=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
             '-s',f'{width}x{height}','-r',str(fps),'-i','pipe:0','-i',str(audio),
             '-t',str(duration),'-c:v','libx264','-preset','veryfast','-crf','23',
             '-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',str(output)]
        process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
        try:
            for frame in range(math.ceil(duration*fps)):
                image=animal_frame(animal,visual_style,frame/fps,width,height)
                process.stdin.write(np.asarray(image).tobytes())
            process.stdin.close()
            if process.wait()!=0:raise RuntimeError('Animal rendering failed')
        except BaseException:
            process.kill();process.wait();raise
    return output
