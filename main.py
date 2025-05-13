from output.tts import TTS
from input.arduino_rfid_reader import handle_rfid_data
from input.arduino_sensor_reader import handle_sensor_data

import serial
import time
import subprocess
import os
import sys

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

        # ✅ UNO B: RFID 아두이노 연결
        try:
            self.arduino_rfid = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
            print("✅ RFID 아두이노 연결 성공")
        except Exception as e:
            print("❌ RFID 보드 연결 실패:", e)
            self.arduino_rfid = None

        # ✅ UNO A: 센서 아두이노 연결
        try:
            self.arduino_sensor = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
            print("✅ 센서 아두이노 연결 성공")
        except Exception as e:
            print("❌ 센서 보드 연결 실패:", e)
            self.arduino_sensor = None

    def run_logic(self):
        read_rfid_now = False  # 무게 변화 감지 시 True로 설정
        try:
            while True:
                # 센서 수신 → 무게 변화 여부 판단
                if self.arduino_sensor and self.arduino_sensor.in_waiting:
                    read_rfid_now = handle_sensor_data(self.arduino_sensor, self.tts)

                # 무게 변화가 감지된 경우만 RFID 리딩
                if read_rfid_now and self.arduino_rfid and self.arduino_rfid.in_waiting:
                    handle_rfid_data(self.arduino_rfid, self.tts)
                    read_rfid_now = False  # 1회만 수행

                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 프로그램 종료 중...")
            if self.flask_process:
                self.flask_process.terminate()
                print("🧹 Flask 서버 프로세스 종료됨")

if __name__ == "__main__":
    cart = SmartCart()
    cart.run_logic()
