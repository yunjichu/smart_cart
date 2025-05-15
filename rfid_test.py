import serial

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
print("✅ 포트 열림, 데이터 수신 대기 중...")

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"[📦 수신] {line}")


