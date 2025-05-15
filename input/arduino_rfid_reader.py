import sys
import os
import time
import sqlite3

# 현재 스크립트가 있는 디렉토리로부터 상대 경로로 web 디렉토리 찾기

sys.path.append(os.path.join(os.getcwd(), 'web'))

from app import add_to_cart1 #y에서 정의한 get_db 함수 호출

def handle_rfid_data(ser, tts):
    try:
        while True:
            if ser.in_waiting == 0:
                time.sleep(0.1)
                continue

            line = ser.readline().decode('utf-8').strip()
            print(f"📡 RFID 수신 데이터: {line}")

            if "UID:" in line:
                uid = line.split("UID:")[1].strip()
                print(f"📦 UID 감지: {uid}")
                add_to_cart1(uid)
                tts.speak(f"RFID 태그 {uid} 읽음")
            else:
                print("❌ 예상된 RFID 형식이 아닙니다:", line)
    except Exception as e:
        print("❌ RFID 데이터 처리 오류:", e)
