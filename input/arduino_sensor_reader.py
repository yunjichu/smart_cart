# input/arduino_sensor_reader.py
import time

def handle_sensor_data(ser, tts, arduino_weight):
    try:
        while True:
            if ser.in_waiting == 0:
                time.sleep(0.1)
                continue

            line = ser.readline().decode('utf-8').strip()
            print(f"📡 센서 수신 데이터: {line}")

            if line.startswith("OBSTACLE:"):
                direction = line.split(":")[1]
                direction_kor = {
                    "left": "왼쪽",
                    "right": "오른쪽",
                    "front": "앞쪽"
                }.get(direction, direction)
                
                print(f"{direction_kor} 방향에서 장애물이 감지되었습니다.")
                tts.speak(f"{direction_kor} 방향에서 장애물이 감지되었습니다.")
                time.sleep(2)  # 음성 안내 간격
            elif line.startswith("Hands off"):
                arduino_weight.write(b"Hands off\n")
            else:
                print("❌ 예상된 센서 형식이 아닙니다:", line)
    except Exception as e:
        print(" 센서 데이터 처리 오류:", e)

