"""Create personalized thumbnails locally; no image-generation API is needed."""
import random
from PIL import Image, ImageDraw
from .video import style, PALETTES, centered


def create_thumbnail(name, job_id, path, content_kind='birthday', visual_style='cartoon'):
    if content_kind == 'animal':
        from .animals import animal_frame
        path.parent.mkdir(parents=True,exist_ok=True)
        animal_frame(name.lower(),visual_style).save(path,'JPEG',quality=90,optimize=True)
        return path
    if content_kind != 'birthday':
        from .ambience import scene
        path.parent.mkdir(parents=True,exist_ok=True)
        scene(content_kind,name).save(path,'JPEG',quality=90,optimize=True)
        return path
    seed, _ = style(job_id)
    bg, accent, secondary = PALETTES[seed % len(PALETTES)]
    width, height = 1080, 1920
    image = Image.new('RGB', (width, height), bg)
    draw = ImageDraw.Draw(image)
    rng = random.Random(seed)
    # Keep decorative confetti outside the central text area.
    for _ in range(130):
        x, y = rng.randrange(width), rng.randrange(height)
        if 230 < x < 850 and 480 < y < 1170:
            continue
        radius = rng.randrange(4, 11)
        draw.ellipse((x-radius, y-radius, x+radius, y+radius),
                     fill=accent if rng.random() < .5 else secondary)
    for x in (140, 940):
        draw.line((x, 400, x+20, 650), fill=accent, width=4)
        draw.ellipse((x-82, 160, x+82, 400), fill=secondary)
    centered(draw, 'HAPPY', 530, 130, accent, width)
    centered(draw, 'BIRTHDAY', 690, 152, 'white', width)
    centered(draw, name, 920, 180, accent, width)
    # Original cake artwork.
    draw.rounded_rectangle((300, 1280, 780, 1480), radius=35, fill=secondary)
    draw.rounded_rectangle((300, 1260, 780, 1320), radius=25, fill=accent)
    for x in (390, 540, 690):
        draw.rectangle((x-8, 1180, x+8, 1260), fill='white')
        draw.ellipse((x-15, 1140, x+15, 1180), fill=accent)
    centered(draw, 'Enjoy your special day!', 1590, 52, 'white', width)
    centered(draw, 'ENJOY YOUR DAY STUDIO', 1770, 36, accent, width)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, 'JPEG', quality=90, optimize=True)
    # Conservative limit for broad compatibility.
    if path.stat().st_size > 2 * 1024 * 1024:
        raise ValueError('Generated thumbnail exceeds 2 MiB')
    return path
