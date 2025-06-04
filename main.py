import serial
import threading
import time
import subprocess
import os
import sys

from output.tts import TTS
from input.arduino_rfid_reader import handle_rfid_data
from input.arduino_sensor_reader import handle_sensor_data
from input.arduino_weight_reader import handle_weight_data
from input.button import button_listener

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
            self.arduino_weight = serial.Serial('', 9600, timeout=1)
            print("✅ 무게 아두이노 연결 성공")
        except Exception as e:
            print("❌ 무게 보드 연결 실패:", e)
            self.arduino_weight = None

    def safe_thread(self, target, name, *args):
        def wrapper():
            try:
                print(f"🔁 {name} 스레드 시작")
                target(*args)
            except Exception as e:
                print(f"❌ {name} 스레드 오류:", e)
        return threading.Thread(target=wrapper, name=name)

    def run_logic(self):
        threads = []

        if self.arduino_sensor:
            threads.append(self.safe_thread(handle_sensor_data, "센서", self.arduino_sensor, self.tts, self.arduino_weight))

        if self.arduino_weight:
            threads.append(self.safe_thread(handle_weight_data, "무게", self.arduino_weight, self.arduino_rfid))

        if self.arduino_rfid:
            threads.append(self.safe_thread(handle_rfid_data, "RFID", self.arduino_rfid, self.tts))
            
         # ✅ 버튼 TTS 기능 스레드 실행 (self.tts 전달)
        threads.append(self.safe_thread(button_listener, "버튼", self.tts))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

if __name__ == "__main__":
    try:
        cart = SmartCart()
        cart.run_logic()
    except Exception as e:
        print("💥 실행 중 오류 발생:", e)
        import traceback
        traceback.print_exc()