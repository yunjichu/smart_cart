import RPi.GPIO as GPIO
import time
import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db')))
from database import get_todays_events

import RPi.GPIO as GPIO
from database import get_todays_events

BUTTON_PIN = 18  # 사용할 GPIO 핀 번호

def register_button_callback(tts, pause_flag):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def callback(channel):
        pause_flag.set()
        print("🔘 버튼이 눌렸습니다.")
        events = get_todays_events()
        if not events:
            tts.speak("오늘 예정된 행사가 없습니다.")
        else:
            for event in events:
                tts.speak(f"오늘의 행사: {event['event_name']} - {event['discount_info']}")
        pause_flag.clear()

    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=callback, bouncetime=300)
