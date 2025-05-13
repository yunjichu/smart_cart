def handle_rfid_data(ser, tts):
    """
    UNO B에서 수신한 RFID UID 데이터를 처리하는 함수
    예상 형식: "READER1:UID123456"
    """
    try:
        # 데이터가 없거나 타임아웃이 발생한 경우 처리
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line and line.startswith("READER"):
                reader, uid = line.split(":")
                print(f"📦 {reader} → UID 감지: {uid}")
                tts.speak(f"{reader}에서 물건이 추가되었습니다.")
            else:
                print("❌ 잘못된 데이터 또는 빈 문자열 수신")
        else:
            print("❌ 데이터 없음")
    except Exception as e:
        print(f"❌ RFID 데이터 처리 오류: {e}")
