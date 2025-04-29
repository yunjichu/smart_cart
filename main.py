# main.py

# 👇 기능 클래스 import (구현은 각각 input/, output/, db/, web/ 에 작성 예정)
from rfid.multi_reader import MultiRFIDReader   # ✅ 변경: 다중 리더기 지원
from input.button import EventButton
from output.tts import TTS
from db.local_db import LocalDB
from web.app import WebServer

import serial      # 아두이노와 시리얼 통신용
import threading   # run_logic과 웹 서버 병렬 실행
import time        # 루프 간 간격 설정용 sleep

class SmartCart:
    def __init__(self):
        # 👉 모듈 초기화 (하드웨어 및 DB, TTS 등)
        self.rfid = MultiRFIDReader()             # ✅ 변경: 3개 리더기 지원 객체
        self.button = EventButton()
        self.tts = TTS()
        self.db = LocalDB()

        # 👉 아두이노 시리얼 포트 연결 (환경에 따라 '/dev/ttyACM0' 또는 'COM3' 등으로 수정)
        try:
            self.arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
            print("✅ 아두이노 시리얼 연결 성공")
        except Exception as e:
            print("❌ 아두이노 연결 실패:", e)
            self.arduino = None

    def run_logic(self):
        while True:
            # 1. 시리얼 데이터가 있는 경우 → 읽기
            if self.arduino and self.arduino.in_waiting > 0:
                try:
                    line = self.arduino.readline().decode('utf-8').strip()
                    print("📦 아두이노 →", line)

                    # 1️⃣ 무게 변화 감지 → RFID 태그 읽기
                    if line.startswith("WEIGHT:"):
                        tags = self.rfid.read_all()  # ✅ 변경된 다중 리더기 처리
                        if tags:
                            for idx, tag in tags.items():
                                self.db.insert_product(tag)
                                name = self.db.get_product_name(tag)
                                self.tts.speak(f"{name}가 장바구니에 담겼습니다.")
                        else:
                            print("⚠ RFID 태그 인식 실패")

                    # 2️⃣ 장애물 감지
                    elif line.startswith("OBSTACLE:"):
                        direction = line.split(":")[1].strip().lower()
                        direction_kor = {
                            "left": "왼쪽",
                            "right": "오른쪽",
                            "front": "앞쪽"
                        }.get(direction, "알 수 없는 방향")
                        self.tts.speak(f"{direction_kor}에 장애물이 감지됩니다.")

                except Exception as e:
                    print("⚠ 시리얼 통신 처리 중 오류:", e)

            # 3. 버튼 입력 감지
            if self.button.is_pressed():
                self.tts.speak("오늘의 행사 상품은 딸기 우유입니다.")

            time.sleep(0.1)  # 루프 딜레이

    def start(self):
        # run_logic() 센서 처리 루프는 별도 스레드로 실행
        threading.Thread(target=self.run_logic).start()
        WebServer().run()  # Flask 웹 실행 (구현 후 작동됨)

if __name__ == "__main__":
    # 프로그램 실행 시작
    SmartCart().start()
