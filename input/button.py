import RPi.GPIO as GPIO
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db')))
from database import get_todays_events

BUTTON_PIN = 18  # 사용할 GPIO 핀 번호

def button_listener(tts, pause_flag):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def callback(channel):  # channel: GPIO 핀 번호 (필수 매개변수)
        pause_flag.set()
        print("🔘 버튼이 눌렸습니다.")
        events = get_todays_events()

        if not events:
            tts.speak("오늘 예정된 행사가 없습니다.")
        else:
            for event in events:
                item_name, event_price, event_rate = event
                tts.speak(
                    f"{item_name}은 {event_rate} 퍼센트 할인 중이며 {event_price}원입니다."
                )

        pause_flag.clear()

    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=callback, bouncetime=300)

    try:
        while True:
            time.sleep(1)  # 무한 대기 유지
    except KeyboardInterrupt:
        GPIO.cleanup()
