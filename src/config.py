from .errors import SafeError
import os

def required(key):
    value = os.environ.get(key, '').strip()
    if not value:
        raise SafeError(f'Missing required secret: {key}')
    return value

def validate_name(name):
    name = ' '.join(name.split())
    if not name or len(name) > 40 or any(not (c.isalpha() or c in " '-.") for c in name):
        raise SafeError('Use a name of 1–40 letters, spaces, apostrophes, hyphens or periods.')
    return name
