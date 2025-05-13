
from gtts import gTTS
import os
import time
import platform

class TTS:
    def __init__(self, lang='ko'):
        self.lang = lang
        self.os_type = platform.system()

    def speak(self, text):
        try:
            tts = gTTS(text=text, lang=self.lang)
            filename = f"tts_{int(time.time())}.mp3"
            tts.save(filename)

            # OS에 따라 재생 명령어 선택
            if self.os_type == "Windows":
                os.system(f"start {filename}")
            elif self.os_type == "Darwin":  # macOS
                os.system(f"afplay {filename}")
            else:  # Linux (라즈베리파이 포함)
                os.system(f"mpg123 {filename}")

            # 재생 후 파일 삭제
            time.sleep(1)
            os.remove(filename)

        except Exception as e:
            print("❌ TTS 오류:", e)
