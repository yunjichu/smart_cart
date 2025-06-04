import sqlite3

# SQLite DB 경로 설정 (필요 시 외부 설정 파일로도 가능)
DATABASE = r'C:\Users\911\Downloads\smart_cart-main\smart_cart-main\db\capstone.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def enable_foreign_keys():
    conn = get_db()
    conn.execute('PRAGMA foreign_keys = ON')
    conn.commit()
    conn.close()

def add_to_cart_by_uid(uid, cart_num=1):
    print(f"🛒 UID {uid}를 DB에 추가 중...")
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO cart (cart_num, item_num, quantity)
            VALUES (?, ?, 1)
            ON CONFLICT(cart_num, item_num) DO UPDATE SET quantity = quantity + 1
        ''', (cart_num, uid))
        conn.commit()
        print(f"[DB] UID {uid} 카트에 추가 완료")
    except sqlite3.Error as e:
        print(f"[DB 오류] {e}")
    finally:
        conn.close()

def get_item_info_by_rfid(rfid_number):
    conn = get_db()
    item = conn.execute('''
        SELECT item_name, item_exp, item_storage
        FROM item
        WHERE item_num = ?
    ''', (rfid_number,)).fetchone()
    conn.close()
    return item
