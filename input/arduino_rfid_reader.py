import sys
import os
import time
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db')))

from database import add_to_cart_by_uid, get_item_info_by_rfid  # DB 함수 사용

# 🧾 현재 장바구니 UID 상태 (라즈베리파이 메모리)
current_uids = set()

# 📥 RFID 명령에 따라 UID 처리
# - READ_ADD: 하나 읽어서 추가
# - READ_REMOVE: 여러 개 읽고 없는 것 제거

def handle_rfid_data(arduino_rfid, tts):
    while True:
        rfid_data = arduino_rfid.readline().decode('utf-8').strip()

        if not rfid_data:
            continue

        print(f"[RFID 수신] {rfid_data}")

        # 무게 증가 시: 하나 읽어서 추가
        if rfid_data.startswith("READ_ADD:"):
            uid = rfid_data.replace("READ_ADD:", "").strip()
            if uid not in current_uids:
                current_uids.add(uid)
                add_to_cart_by_uid(uid)

                item = get_item_info_by_rfid(uid)
                if item:
                    item_name = item["item_name"]
                    item_expiry = item["item_exp"]
                    item_storage = item["item_storage"]
                    tts.speak(f"{item_name}, 유통기한 {item_expiry}, 보관: {item_storage}")
                else:
                    tts.speak("등록되지 않은 물품입니다.")
            else:
                print(f"[무시됨] {uid} 이미 장바구니에 있음")

        # 무게 감소 시: 여러 개 읽고 없는 것 제거
        elif rfid_data.startswith("READ_REMOVE_START"):
            print("[RFID] 다중 읽기 시작")
            read_uids = set()
            start = time.time()

            while time.time() - start < 5:
                if arduino_rfid.in_waiting:
                    line = arduino_rfid.readline().decode('utf-8').strip()
                    if line.startswith("UID:"):
                        uid = line.replace("UID:", "").strip()
                        if uid:
                            read_uids.add(uid)

            to_remove = current_uids - read_uids
            for uid in to_remove:
                current_uids.remove(uid)
                tts.speak(f"{uid} 장바구니에서 제거되었습니다.")
                # 여기서 DB 제거 함수 호출 필요: remove_from_cart_by_uid(uid)

        else:
            print(f"[경고] 알 수 없는 RFID 명령 또는 형식: {rfid_data}")