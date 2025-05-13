import sys
import os
import time
import sqlite3

# app.py가 위치한 경로를 절대 경로로 추가
sys.path.append('/home/rpi4/Desktop/smart_cart/web')

from app import add_to_cart #y에서 정의한 get_db 함수 호출

def handle_rfid_data(ser):
    """
    UNO B에서 수신한 RFID UID 데이터를 처리하는 함수
    예상 형식: "READER1 UID: XXXXXXXX"
    """
    try:
        while ser.in_waiting == 0:
            time.sleep(0.1)  # 시리얼 포트에서 데이터가 들어올 때까지 대기

        line = ser.readline().decode('utf-8').strip()  # 데이터 읽기
        print(f"수신된 데이터: {line}")  # 디버깅: 수신된 데이터 출력

        # 데이터 형식이 "READER1 UID: XXXXX"와 같은 형식인지 확인
        if "UID:" in line:
            parts = line.split(" UID: ")  # "READER1 UID: XXXXX"를 분리
            if len(parts) == 2:
                reader = parts[0]  # READER1
                uid = parts[1]  # UID 값
                print(f"📦 {reader} → UID 감지: {uid}")

                # DB에 UID 추가 (app.py에서 정의한 add_to_cart 함수 호출)
                add_to_cart(uid)  # app.py의 add_to_cart 함수 호출

                # TTS로 알림
                print(f"✔️ UID {uid}가 {reader}에서 감지됨!")
        else:
            print(f"❌ 잘못된 데이터 형식: '{line}'")
    except Exception as e:
        print(f"❌ RFID 데이터 처리 오류: {e}")

