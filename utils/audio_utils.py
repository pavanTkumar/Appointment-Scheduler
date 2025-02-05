import speech_recognition as sr
from gtts import gTTS
import os
import tempfile

class AudioManager:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def record_audio(self, duration=5):
        with sr.Microphone() as source:
            audio = self.recognizer.record(source, duration=duration)
        return audio

    def speech_to_text(self, audio_data):
        try:
            text = self.recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return None

    def text_to_speech(self, text):
        tts = gTTS(text=text, lang='en')
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name