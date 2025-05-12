import serial

# UNO가 연결된 포트로 설정 (ttyUSB0, ttyACM0 등 상황에 맞게 변경)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

print("아두이노에서 UID 수신 대기 중...")

try:
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith("READER"):
            reader, uid = line.split(":")
            print(f"{reader} 에서 태그 감지됨 → UID: {uid}")
except KeyboardInterrupt:
    print("종료합니다.")

