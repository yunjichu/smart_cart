import time
from gtts import gTTS
import os

class TTS:
    def __init__(self, lang='ko'):
        self.lang = lang

    def speak(self, text):
        try:
            tts = gTTS(text=text, lang=self.lang)
            filename = f"/tmp/tts_{int(time.time())}.mp3"
            tts.save(filename)

            # VLC를 사용하여 재생
            os.system(f"cvlc --play-and-exit {filename}")

            os.remove(filename)

        except Exception as e:
            print("❌ TTS 오류:", e)
