import time
import os
import serial
import subprocess
import sys
from output.tts import TTS
from input.arduino_rfid_reader import handle_rfid_data
from input.arduino_sensor_reader import handle_sensor_data

def get_serial_port():
    """
    시스템에서 연결된 모든 시리얼 포트 리스트 출력
    자동으로 첫 번째 포트를 사용하도록 설정
    """
    ports = [f"/dev/{dev}" for dev in os.listdir('/dev') if dev.startswith('ttyUSB') or dev.startswith('ttyACM')]
    if ports:
        return ports[0]  # 첫 번째 포트를 사용
    else:
        raise Exception("시리얼 포트를 찾을 수 없습니다.")

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
            self.arduino_rfid = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
            print(f"✅ RFID 아두이노 연결 성공: ")
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
        #read_rfid_now = False  # 무게 감지 없이 RFID를 리딩할 준비 상태
        last_rfid_time = time.time()  # 마지막 RFID 리딩 시간 추적

        try:
            while True:
                # 센서 수신 → RFID 리딩을 바로 실행
                if self.arduino_rfid and self.arduino_sensor.in_waiting:
                    handle_rfid_data(self.arduino_rfid)

                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n🛑 프로그램 종료 중...")
            if self.flask_process:
                self.flask_process.terminate()
                print("🧹 Flask 서버 프로세스 종료됨")

if __name__ == "__main__":
    cart = SmartCart()
    cart.run_logic()
