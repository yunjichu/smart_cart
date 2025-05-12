# input/arduino_rfid_reader.py

def handle_rfid_data(ser, tts):
    """
    UNO B에서 수신한 RFID UID 데이터를 처리하는 함수
    예상 형식: "READER1:UID123456"
    """
    try:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("READER"):
            reader, uid = line.split(":")
            print(f"📦 {reader} → UID 감지: {uid}")
            tts.speak(f"{reader}에서 물건이 추가되었습니다.")
    except Exception as e:
        print("❌ RFID 데이터 처리 오류:", e)
