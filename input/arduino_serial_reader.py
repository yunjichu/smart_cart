import serial
import time

def read_serial_data():
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2)

    try:
        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                if not line:
                    continue

                if line in ['left', 'front', 'right']:
                    print(f"[⚠️ 장애물] 방향: {line}")
                else:
                    try:
                        weight = float(line)
                        print(f"[⚖️ 무게 변화 감지] {weight:.2f} g")
                    except ValueError:
                        print(f"[⚠️ 예외] 파싱 실패: {line}")
    except KeyboardInterrupt:
        ser.close()
