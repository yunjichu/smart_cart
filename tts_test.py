from output.tts import TTS
import time

tts = TTS()

#tts.speak("이것은 테스트 음성입니다. 안녕하세요!")

from output.tts import TTS

tts = TTS()

# 여러 문장을 리스트로 준비
messages = [
    "딸기 우유가 장바구니에 담겼습니다.",
    "초콜릿이 장바구니에 담겼습니다.",
    "오늘의 행사 상품은 식빵입니다."
]

# 리스트를 한 문장으로 이어붙이기 (끊기지 않도록)
merged_message = " ".join(messages)

# 한 번에 speak (gTTS가 한 mp3로 처리)
tts.speak(merged_message)
