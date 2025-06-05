# input/arduino_sensor_reader.py
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db')))
from database import get_todays_events

def handle_sensor_data(ser, tts, arduino_weight):
    try:
       while True:

            if ser.in_waiting == 0:
                time.sleep(0.1)
                continue
            
            line = ser.readline().decode('utf-8').strip()
            print(f"📡 센서 수신 데이터: {line}")

            if line.startswith("Button"):
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
                        
            if line.startswith("OBSTACLE:"):
                direction = line.split(":")[1]
                direction_kor = {
                    "left": "왼쪽",
                    "right": "오른쪽",
                    "front": "앞쪽"
                }.get(direction, direction)
                
                print(f"{direction_kor} 방향 장애물 감지")
                tts.speak(f"{direction_kor} 방향 장애물 감지")
                time.sleep(2)  # 음성 안내 간격
            elif line.startswith("Hands off"):
                arduino_weight.write(b"Hands off\n")
                arduino_weight.flush()
            else:
                print("❌ 예상된 센서 형식이 아닙니다:", line)
    except Exception as e:
        print(" 센서 데이터 처리 오류:", e) 

