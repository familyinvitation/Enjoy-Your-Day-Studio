import os
from google.cloud import texttospeech

def create_voice(name, message, path, credentials):
    client = texttospeech.TextToSpeechClient(credentials=credentials)
    response = client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=f'Happy Birthday {name}! {message} Enjoy your special day!'),
        voice=texttospeech.VoiceSelectionParams(language_code='en-US',
            name=os.getenv('TTS_VOICE', 'en-US-Neural2-F'), ssml_gender=texttospeech.SsmlVoiceGender.FEMALE),
        audio_config=texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                                               speaking_rate=0.95))
    path.write_bytes(response.audio_content)
