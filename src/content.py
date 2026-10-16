"""Content selection; the original seven-column birthday queue remains valid."""
from .config import validate_name

CHANNEL = 'Enjoy Your Day Studio'
TAGLINE = 'Celebrate. Relax. Enjoy Your Day.'

def content_settings(row):
    cells = list(row) + [''] * 10
    kind = cells[7].strip().lower() or 'birthday'
    if kind not in ('birthday', 'rain', 'music', 'animal'):
        raise ValueError('Type must be birthday, rain, music or animal')
    label = validate_name(cells[0]) if kind == 'birthday' else ' '.join(cells[0].split())
    if not label or len(label) > 70 or any(ord(c) < 32 or c in '<>' for c in label):
        raise ValueError('Use a label of 1–70 characters without angle brackets or control characters')
    minimum, maximum, default = {
        'birthday': (60, 600, 90),
        'rain': (1800, 7200, 1800),
        'music': (1800, 7200, 1800),
        'animal': (10, 600, 60),
    }[kind]
    duration = int(cells[8] or str(default))
    # Old sample rows used 60 seconds: automatically upgrade shorter rain/music requests.
    if kind in ('rain', 'music') and 0 < duration < minimum:
        duration = minimum
    if not minimum <= duration <= maximum:
        raise ValueError(f'{kind} duration must be {minimum}–{maximum} seconds')
    return kind, label, duration

def metadata(kind, label, visual_style='cartoon'):
    if kind == 'birthday':
        title = f'Happy Birthday {label} | {CHANNEL}'
        description = f'Happy Birthday {label}! Personalized birthday lyrics read aloud over instrumental background music, with repeated birthday choruses. Wishing you happiness, laughter and a wonderful year ahead.'
        tags = ['happy birthday', f'happy birthday {label}', 'birthday wishes']
        category = '24'
    elif kind == 'animal':
        title = f'{label.title()} | {visual_style.title()} Animal Animation | {CHANNEL}'
        description = f'An original animated illustration of a {label.lower()} in {visual_style} style, with gentle generated instrumental audio. This is illustrated animation, not live animal footage.'
        tags = [label.lower(), 'animal animation', visual_style, 'animated animals']
        category = '15'
    else:
        title = f'{label} | {CHANNEL}'
        description = ('Digitally synthesized rain ambience for a peaceful break. No narration.' if kind == 'rain'
                       else 'Procedurally composed gentle instrumental tones for quiet moments. No narration.')
        tags = ['rain sounds', 'nature ambience', 'relaxation'] if kind == 'rain' else ['relaxing music', 'gentle instrumental', 'relaxation']
        category = '10' if kind == 'music' else '24'
    return {'title': title[:100], 'description': f'{description}\n\n{CHANNEL}\n{TAGLINE}',
            'tags': tags, 'categoryId': category}
