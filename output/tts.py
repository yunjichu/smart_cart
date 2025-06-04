import time
from gtts import gTTS
import pygame
import os

class TTS:
    def __init__(self, lang='ko'):
        self.lang = lang
        pygame.mixer.init()

    def speak(self, text):
        try:
            tts = gTTS(text=text, lang=self.lang)
            filename = f"/tmp/tts_{int(time.time())}.mp3"
            tts.save(filename)

            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            os.remove(filename)

        except Exception as e:
            print("❌ TTS 오류:", e)
