import serial
import threading
import time
import subprocess
import os
import sys

from output.tts import TTS
from input.arduino_sensor_reader import handle_sensor_data
from input.arduino_weight_reader import handle_weight_data

class SmartCart:
    def __init__(self):
        self.tts = TTS()

        # ✅ Flask 웹 서버 실행
        try:
            flask_path = os.path.join("web", "app.py")
            python_exec = sys.executable
            self.flask_process = subprocess.Popen(
                [python_exec, flask_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("🚀 Flask 웹 서버 실행됨")
        except Exception as e:
            print("❌ Flask 실행 실패:", e)
            self.flask_process = None

        # ✅ UNO A: 센서용 아두이노 연결
        try:
            self.arduino_sensor = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
            print("✅ 센서 아두이노 연결 성공")
        except Exception as e:
            print("❌ 센서 보드 연결 실패:", e)
            self.arduino_sensor = None

        # ✅ UNO B: RFID 아두이노 연결
        try:
            self.arduino_rfid = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            print("✅ RFID 아두이노 연결 성공")
        except Exception as e:
            print("❌ RFID 보드 연결 실패:", e)
            self.arduino_rfid = None

        # ✅ UNO C: 무게 아두이노 연결
        try:
            self.arduino_weight = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
            print("✅ 무게 아두이노 연결 성공")
        except Exception as e:
            print("❌ 무게 보드 연결 실패:", e)
            self.arduino_weight = None

    

    def run_logic(self):
         # ✅ 센서 스레드
        if self.arduino_sensor and self.arduino_weight:
            threading.Thread(
                target=handle_sensor_data,
                args=(self.arduino_sensor, self.tts, self.arduino_weight),
                name="센서스레드"
            ).start()

        # ✅ 무게 → RFID
        if self.arduino_weight and self.arduino_rfid:
            handle_weight_data(self.arduino_weight, self.arduino_rfid, self.tts)


if __name__ == "__main__":
    try:
        cart = SmartCart()
        cart.run_logic()
    except Exception as e:
        print("💥 실행 중 오류 발생:", e)
        import traceback
        traceback.print_exc()