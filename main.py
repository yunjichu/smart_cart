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

        # ✅ UNO A: 센서 아두이노 연결 (사용하지 않음)
        self.arduino_sensor = None

    def run_logic(self):
        last_rfid_time = time.time()  # 마지막 RFID 리딩 시간 추적

        try:
            while True:
                # RFID 리딩을 무조건 시도하도록 수정
                if self.arduino_rfid and self.arduino_rfid.in_waiting:
                    handle_rfid_data(self.arduino_rfid, self.tts)  # RFID 태그 리딩
                    last_rfid_time = time.time()  # RFID 리딩 후 시간 갱신

                # 타임아웃 처리: 일정 시간 동안 리딩이 없으면 다시 시작
                if time.time() - last_rfid_time > 5:  # 5초 후 다시 리딩
                    print("❌ RFID 태그를 읽지 못했습니다. 다시 시도 중...")

                time.sleep(0.1)  # 과도한 CPU 사용 방지
        except KeyboardInterrupt:
            print("\n🛑 프로그램 종료 중...")
            if self.flask_process:
                self.flask_process.terminate()
                print("🧹 Flask 서버 프로세스 종료됨")

if __name__ == "__main__":
    cart = SmartCart()
    cart.run_logic()
