# input/arduino_sensor_reader.py

# last_weight = None  # 전역 변수로 마지막 무게 저장
# THRESHOLD = 100.0   # 무게 변화 기준 (100g)

def handle_sensor_data(ser, tts):
    """
    UNO A에서 수신한 센서(장애물) 데이터를 처리하는 함수
    예상 형식:
      - "OBSTACLE:left"
    """
    try:
        line = ser.readline().decode('utf-8').strip()
        
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
            
            # TTS로 장애물 감지 음성 안내
            tts.speak(f"장애물 감지: {direction} 방향")  # 장애물 방향을 TTS로 안내
    except Exception as e:
        print("❌ 센서 데이터 처리 오류:", e)
    return False
