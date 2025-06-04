import sys
import os
import time
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db')))

from database import add_to_cart_by_uid, get_item_info_by_rfid, remove_from_cart_by_uid  # DB 함수 사용

# 🧾 현재 장바구니 UID 상태
current_uids = set()

def handle_rfid_data(arduino_rfid, tts):
    while True:
        rfid_data = arduino_rfid.readline().decode('utf-8').strip()

        if not rfid_data:
            continue

        print(f"[RFID 수신] {rfid_data}")

        parts = rfid_data.split()

        # 형식: READER1 ADD 04AABBCCDD
        if len(parts) == 3 and parts[0].startswith("READER"):
            reader = parts[0]
            action = parts[1]
            uid = parts[2]

            if action == "ADD":
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

            elif action == "REMOVE":
                if uid in current_uids:
                    current_uids.remove(uid)
                    remove_from_cart_by_uid(uid)
                    tts.speak(f"{uid} 장바구니에서 제거되었습니다.")
                else:
                    print(f"[무시됨] {uid} 장바구니에 없음")

        else:
            print(f"[경고] 알 수 없는 형식: {rfid_data}")
