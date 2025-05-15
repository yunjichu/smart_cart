# input/arduino_sensor_reader.py
import time
# last_weight = None  # 전역 변수로 마지막 무게 저장
# THRESHOLD = 100.0   # 무게 변화 기준 (100g)

def handle_sensor_data(ser, tts):
    try:
<<<<<<< HEAD
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
=======
        line = ser.readline().decode('utf-8').strip()
        print(line)
        
        # if line.startswith("WEIGHT:"):
        #     weight = float(line.split(":")[1])
        #     print(f"⚖️ 무게 감지: {weight}g")
        #     if last_weight is None:
        #         last_weight = weight
        #         return False
        #     if abs(weight - last_weight) > THRESHOLD:
        #         print("📦 무게 변화 감지됨 → RFID 리딩")
        #         last_weight = weight
        #         return True
        #     last_weight = weight
        
        if line.startswith("OBSTACLE:"):
            direction = line.split(":")[1]
            print(f"🚧 장애물 감지: {direction} 방향")
            
            ser.close()
            # TTS로 장애물 감지 음성 안내
            tts.speak(f"장애물 감지: {direction} 방향")  # 장애물 방향을 TTS로 안내
            time.sleep(2)
            ser.open()
        else:
            print("❌ 예상된 데이터 형식이 아닙니다.")  # 장애물 데이터 형식이 아닌 경우
            
>>>>>>> 1507df2 (14g)
    except Exception as e:
        print("❌ 센서 데이터 처리 오류:", e)

