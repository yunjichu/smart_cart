#database.py
import sqlite3
import datetime

#DATABASE = r'/home/rpi4/Desktop/smart_cart/db/capstone.sqlite3'
DATABASE = r'C:\Users\chu\Desktop\smart_cart\db\capstone.sqlite3'

def get_db():
    """
    SQLite 데이터베이스에 연결하는 함수
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

#@app.before_request
def enable_foreign_keys():
    """
    요청 전에 SQLite에서 외래 키를 활성화
    """
    conn = get_db()
    conn.execute('PRAGMA foreign_keys = ON')
    conn.commit()
    conn.close()
    
def get_cart_uids(cart_num=1):
    """
    장바구니에 있는 모든 UID(item_num) 목록 조회
    """
    conn = get_db()
    try:
        rows = conn.execute('SELECT item_num FROM cart WHERE cart_num = ?', (cart_num,)).fetchall()
        return [row['item_num'] for row in rows]
    finally:
        conn.close()

def add_to_cart_by_uid(uid):
    print(f"UID {uid}를 DB에 추가 중...")
    conn = get_db()
    try:
        conn.execute(''' 
            INSERT INTO cart (cart_num, item_num, quantity) 
            VALUES (?, ?, 1)
            ON CONFLICT(cart_num, item_num) DO NOTHING
        ''', (1, uid))  # 이미 있으면 무시 (DO NOTHING)
        conn.commit()
        print(f"[DB] UID {uid} 카트에 추가 완료 또는 이미 존재")
    except sqlite3.Error as e:
        print(f"[DB 오류] {e}")
    finally:
        conn.close()

def remove_from_cart_by_uid(uid):
    print(f"UID {uid}를 장바구니에서 제거 중...")
    """카트에 UID 제거거하는 함수"""
    conn = get_db()
    try:
        row = conn.execute('SELECT quantity FROM cart WHERE cart_num = ? AND item_num = ?', (1, uid)).fetchone()
        if row:
            if row['quantity'] > 1:
                conn.execute('UPDATE cart SET quantity = quantity - 1 WHERE cart_num = ? AND item_num = ?', (1, uid))
            else:
                conn.execute('DELETE FROM cart WHERE cart_num = ? AND item_num = ?', (1, uid))
            conn.commit()
            print(f"[DB] UID {uid} 제거 성공")
            return True
        else:
            print(f"[DB] UID {uid} 장바구니에 없음")
            return False
    except sqlite3.Error as e:
        print(f"[DB 오류] {e}")
        return False
    finally:
        conn.close()

def get_item_info_by_rfid(rfid_number):
    """
    RFID 번호로 물품 정보를 조회
    """
    conn = get_db()
    try:
        item = conn.execute('''
            SELECT item_name, item_exp, item_storage
            FROM item
            WHERE item_num = ?
        ''', (rfid_number,)).fetchone()
        return item
    finally:
        conn.close()

def add_or_update_event(data):
    """
    할인 행사 정보를 DB에 추가하거나 업데이트
    """
    conn = get_db()
    try:
        # item 존재 여부 확인
        item_exists = conn.execute('SELECT 1 FROM item WHERE item_num = ?', (data['item_num'],)).fetchone()
        if not item_exists:
            return False, "존재하지 않는 물품번호입니다."

        origin_price = data['origin_price']
        event_price = data['event_price']
        event_rate = round((origin_price - event_price) / origin_price * 100)
        period = data['event_period']

        conn.execute('''
            INSERT INTO event (item_num, origin_price, event_price, event_rate, event_period)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(item_num) DO UPDATE SET
                origin_price = ?,
                event_price = ?,
                event_rate = ?,
                event_period = ?
        ''', (
            data['item_num'],
            origin_price,
            event_price,
            event_rate,
            period,
            origin_price,
            event_price,
            event_rate,
            period
        ))
        conn.commit()
        return True, None
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        conn.close()
        
def get_todays_events():
    conn = get_db()
    today = datetime.date.today()

    cursor = conn.execute("""
        SELECT i.item_name, e.origin_price, e.event_price, e.event_rate, e.event_period
        FROM event e
        JOIN item i ON e.item_num = i.item_num
    """)
    all_events = cursor.fetchall()
    conn.close()

    todays_events = []

    for item_name, origin_price, event_price, event_rate, event_period in all_events:
        try:
            start_str, end_str = event_period.split('~')
            start_date = datetime.datetime.strptime(start_str.strip(), "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_str.strip(), "%Y-%m-%d").date()

            if start_date <= today <= end_date:
                todays_events.append((item_name, origin_price, event_price, event_rate, event_period))
        except ValueError:
            # 날짜 형식이 잘못된 경우 건너뜀
            continue

    return todays_events