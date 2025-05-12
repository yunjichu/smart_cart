# input/arduino_sensor_reader.py

def handle_sensor_data(ser, tts):
    """
    UNO A에서 수신한 센서(무게/장애물) 데이터를 처리하는 함수
    예상 형식:
      - "WEIGHT:1234.56"
      - "OBSTACLE:left"
    """
    try:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("WEIGHT:"):
            weight = line.split(":")[1]
            print(f"⚖️ 무게 감지: {weight}g")
            # 필요시 TTS: tts.speak(f"{weight}그램입니다.")
        elif line.startswith("OBSTACLE:"):
            direction = line.split(":")[1]
            print(f"🚧 장애물 감지: {direction} 방향")
            tts.speak(f"{direction}에 장애물이 있습니다.")
    except Exception as e:
        print("❌ 센서 데이터 처리 오류:", e)
