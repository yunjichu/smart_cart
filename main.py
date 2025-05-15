import serial
import threading
import time
import subprocess
import os
import sys

from output.tts import TTS
from input.arduino_rfid_reader import handle_rfid_data
from input.arduino_sensor_reader import handle_sensor_data

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

    def run_logic(self):
        threads = []

        if self.arduino_sensor:
            t_sensor = threading.Thread(target=handle_sensor_data, args=(self.arduino_sensor, self.tts))
            t_sensor.start()
            threads.append(t_sensor)

        if self.arduino_rfid:
            t_rfid = threading.Thread(target=handle_rfid_data, args=(self.arduino_rfid, self.tts))
            t_rfid.start()
            threads.append(t_rfid)

        for t in threads:
            t.join()

if __name__ == "__main__":
    cart = SmartCart()
    cart.run_logic()
