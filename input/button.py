import RPi.GPIO as GPIO
import time
import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db')))
from database import get_db

BUTTON_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def get_todays_events():
    """
    오늘 날짜의 행사 정보를 DB에서 조회
    """
    conn = get_db()
    today = datetime.date.today().isoformat()
    cursor = conn.execute("SELECT event_name, discount_info FROM events WHERE event_date = ?", (today,))
    results = cursor.fetchall()
    conn.close()
    return results

def button_listener(tts):
    """
    버튼이 눌렸을 때 TTS로 행사 정보를 읽어주는 리스너
    """
    def button_callback(channel):
        print("🔘 버튼이 눌렸습니다.")
        events = get_todays_events()
        if not events:
            tts.speak("오늘 예정된 행사가 없습니다.")
        else:
            for event in events:
                message = f"오늘의 행사: {event['event_name']} - {event['discount_info']}"
                print(f"TTS: {message}")
                tts.speak(message)

    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)
    print("👂 버튼 이벤트 대기 중...")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
