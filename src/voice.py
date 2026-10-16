"""Local Piper narration. Downloads public model files once; synthesis runs offline."""
import os
import wave
from functools import lru_cache
from pathlib import Path
from urllib.request import urlopen
import shutil

VOICE = 'en_US-ljspeech-medium'
BASE = 'https://huggingface.co/rhasspy/piper-voices/resolve/c10ece1aade47bb51c153c893d14e5bf8e5b7117/en/en_US/ljspeech/medium/'


def ensure_voice():
    directory = Path(os.getenv('PIPER_MODEL_DIR', '.cache/piper'))
    directory.mkdir(parents=True, exist_ok=True)
    for filename in (VOICE+'.onnx', VOICE+'.onnx.json', 'MODEL_CARD'):
        path=directory/filename
        if not path.is_file() or path.stat().st_size == 0:
            temporary=path.with_suffix(path.suffix+'.part')
            try:
                with urlopen(BASE+filename, timeout=60) as response, temporary.open('wb') as target:
                    shutil.copyfileobj(response,target)
                if temporary.stat().st_size == 0:
                    raise RuntimeError('Empty Piper model download')
                temporary.replace(path)
            finally:
                temporary.unlink(missing_ok=True)
    return directory/(VOICE+'.onnx')


@lru_cache(maxsize=1)
def load_voice(model):
    from piper import PiperVoice
    return PiperVoice.load(model, use_cuda=False)


def create_voice(name, message, path):
    model=ensure_voice()
    voice=load_voice(str(model))
    path.parent.mkdir(parents=True,exist_ok=True)
    text=f'Happy Birthday {name}! {message} Enjoy your special day!'
    with wave.open(str(path),'wb') as output:
        voice.synthesize_wav(text,output)
    with wave.open(str(path),'rb') as output:
        if output.getnframes()==0 or output.getnchannels()!=1 or output.getsampwidth()!=2:
            raise RuntimeError('Piper produced an invalid narration WAV')
    return path
