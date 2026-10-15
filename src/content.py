"""Content selection; the original seven-column birthday queue remains valid."""
from .config import validate_name

CHANNEL = 'Enjoy Your Day Studio'
TAGLINE = 'Celebrate. Relax. Enjoy Your Day.'

def content_settings(row):
    cells = list(row) + [''] * 10
    kind = cells[7].strip().lower() or 'birthday'
    if kind not in ('birthday', 'rain', 'music'):
        raise ValueError('Type must be birthday, rain or music')
    label = validate_name(cells[0]) if kind == 'birthday' else ' '.join(cells[0].split())
    if not label or len(label) > 70 or any(ord(c) < 32 or c in '<>' for c in label):
        raise ValueError('Use a label of 1–70 characters without angle brackets or control characters')
    duration = 60
    if kind != 'birthday':
        duration = int(cells[8] or '60')
        if not 10 <= duration <= 600:
            raise ValueError('Rain/music duration must be 10–600 seconds')
    return kind, label, duration

def metadata(kind, label):
    if kind == 'birthday':
        title = f'Happy Birthday {label} | {CHANNEL}'
        description = f'Happy Birthday {label}! Wishing you happiness, laughter and a wonderful year ahead.'
        tags = ['happy birthday', f'happy birthday {label}', 'birthday wishes']
        category = '24'
    else:
        title = f'{label} | {CHANNEL}'
        description = ('Digitally synthesized rain ambience for a peaceful break. No narration.' if kind == 'rain'
                       else 'Procedurally composed gentle instrumental tones for quiet moments. No narration.')
        tags = ['rain sounds', 'nature ambience', 'relaxation'] if kind == 'rain' else ['relaxing music', 'gentle instrumental', 'relaxation']
        category = '10' if kind == 'music' else '24'
    return {'title': title[:100], 'description': f'{description}\n\n{CHANNEL}\n{TAGLINE}',
            'tags': tags, 'categoryId': category}
