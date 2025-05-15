# input/arduino_sensor_reader.py
import time
# last_weight = None  # 전역 변수로 마지막 무게 저장
# THRESHOLD = 100.0   # 무게 변화 기준 (100g)

def handle_sensor_data(ser, tts):
    try:
        while True:
            if ser.in_waiting == 0:
                time.sleep(0.1)
                continue

            line = ser.readline().decode('utf-8').strip()
            print(f"📡 센서 수신 데이터: {line}")

            if line.startswith("OBSTACLE:"):
                direction = line.split(":")[1]
                print(f"🚧 장애물 감지: {direction} 방향")
                tts.speak(f"장애물 감지: {direction} 방향")
                time.sleep(2)  # 음성 안내 간격
            else:
                print("❌ 예상된 센서 형식이 아닙니다:", line)
    except Exception as e:
<<<<<<< HEAD
        print(" 센서 데이터 처리 오류:", e)
        
=======
        print("센서 데이터 처리 오류: ",e)
>>>>>>> 613e9db7c9df5e4744cafa7a06244ef353672ddf

