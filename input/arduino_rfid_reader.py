import sys
import os
import time
import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db')))

from database import get_cart_uids, add_to_cart_by_uid, remove_from_cart_by_uid, get_item_info_by_rfid  # DB 함수 사용

# RFID 리딩 시점에서 감지한 UID
scanned_uid = None

def handle_rfid_data(arduino_rfid, tts):
    global scanned_uid
    rfid_data = arduino_rfid.readline().decode('utf-8').strip()
    print(rfid_data)

    if not rfid_data:
        print("잘못된 데이터\n")

    print(f"[RFID 수신] {rfid_data}")

    parts = rfid_data.split()

    # 형식: READER1 ADD 04AABBCCDD
    if len(parts) == 3 and parts[0].startswith("READER"):
        reader = parts[0]
        action = parts[1]
        uid = parts[2]
          

        if action == "ADD":
            item = get_item_info_by_rfid(uid)
            if item:
                item_name = item["item_name"]
            cart_uids = set(get_cart_uids())
            if uid not in cart_uids:
                add_to_cart_by_uid(uid)

                if item:
                    item_expiry = item["item_exp"]
                    item_storage = item["item_storage"]
                    tts.speak(f"{item_name}, 유통기한 {item_expiry}, 보관: {item_storage}")
                else:
                    tts.speak("등록되지 않은 물품입니다.")
            else:
                print(f"[무시됨] {item_name} 장바구니에 있음")

        elif action == "REMOVE":
            scanned_uid = uid
            cart_uids = set(get_cart_uids())
            for uid_in_cart in cart_uids:
                if uid_in_cart != scanned_uid:
                    item = get_item_info_by_rfid(uid_in_cart)
                    if item:
                        item_name = item["item_name"]
                    remove_from_cart_by_uid(uid_in_cart)
                    tts.speak(f"{item_name}이 장바구니에서 제거되었습니다.")
    else:
        cart_uids = set(get_cart_uids())
        for uid_in_cart in cart_uids:
            if uid_in_cart != None:
                item = get_item_info_by_rfid(uid_in_cart)
                if item:
                    item_name = item["item_name"]
                remove_from_cart_by_uid(uid_in_cart)
                tts.speak(f"{item_name}이 장바구니에서 제거되었습니다.")
 
