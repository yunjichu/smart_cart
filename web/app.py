from flask import Flask, render_template, request, jsonify
from db import get_db, enable_foreign_keys, add_to_cart_by_uid, get_item_info_by_rfid
import sqlite3
import os
import threading
import serial
import time

# 데이터베이스 파일 경로 설정
# 필요에 따라 경로를 환경 변수나 설정 파일로 분리할 수 있습니다.
DATABASE = r'C:\Users\911\Downloads\smart_cart-main\smart_cart-main\db\capstone.sqlite3'

def get_db():
    """
    SQLite 데이터베이스에 연결하는 함수
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def enable_foreign_keys():
    """
    SQLite 외래 키 활성화
    """
    conn = get_db()
    conn.execute('PRAGMA foreign_keys = ON')
    conn.commit()
    conn.close()

def add_to_cart_by_uid(uid, cart_num=1):
    """
    RFID UID를 사용하여 카트에 물품 추가
    """
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
    """
    RFID 번호로 물품 정보를 조회
    """
    conn = get_db()
    item = conn.execute('''
        SELECT item_name, item_exp, item_storage
        FROM item
        WHERE item_num = ?
    ''', (rfid_number,)).fetchone()
    conn.close()
    return item
✅ app.py에서 수정할 부분
맨 위에 import 추가:

python
코드 복사
from db import get_db, enable_foreign_keys, add_to_cart_by_uid, get_item_info_by_rfid
기존의 get_db(), enable_foreign_keys(), add_to_cart1(), get_item_info() 등 DB 관련 함수들을 삭제합니다.

/api/items/<rfid_number> 경로 함수는 이렇게 수정하세요:

python
코드 복사
@app.route('/api/items/<rfid_number>', methods=['GET'])
def get_item_info(rfid_number):
    item = get_item_info_by_rfid(rfid_number)
    if item:
        return jsonify({
            "item_name": item["item_name"],
            "item_exp": item["item_exp"],
            "item_storage": item["item_storage"]
        })
    else:
        return jsonify({"error": "해당 물품을 찾을 수 없습니다."}), 404
@app.before_request 부분은 enable_foreign_keys()를 호출하도록 유지합니다:

python
코드 복사
@app.before_request
def before_request():
    enable_foreign_keys()
🔄 결과
app.py는 Flask 라우팅 및 뷰 처리에 집중

db.py는 모든 데이터베이스 작업을 관리

유지보수 및 테스트 용이성 증가

필요하다면 models.py, config.py 등을 따로 분리해 더 구조화할 수도 있습니다. 원하시면 그것도 도와드릴게요!



나의 말:
그러면 app.py 코드 전체로 다시 보내줄 수 있어?

ChatGPT의 말:
물론입니다! 아래는 DB 관련 코드를 분리한 새로운 app.py 전체 코드입니다. 분리된 DB 함수는 db.py에서 관리되며, app.py는 라우팅과 로직 중심으로 깔끔하게 정리되어 있습니다.

✅ app.py (Flask 애플리케이션)
python
코드 복사
from flask import Flask, render_template, request, jsonify
from db import get_db, enable_foreign_keys, add_to_cart_by_uid, get_item_info_by_rfid
import sqlite3

app = Flask(__name__)

@app.before_request
def before_request():
    """
    요청 전에 SQLite 외래 키 활성화
    """
    enable_foreign_keys()

@app.route('/')
def index():
    """
    메인 페이지
    """
    total = 10000  # 예시 값
    discount = 2000  # 예시 값
    return render_template('main.html', total=total, discount=discount)

@app.route('/items', methods=['GET'])
def items_page():
    return render_template('items.html')

@app.route('/events', methods=['GET'])
def events_page():
    return render_template('events.html')

@app.route('/transactions', methods=['GET'])
def transactions_page():
    return render_template('transactions.html')

@app.route('/api/items', methods=['POST'])
def register_item():
    data = request.json
    conn = get_db()
    try:
        conn.execute(''' 
            INSERT INTO item (item_num, item_name, item_price, item_size, item_storage, item_exp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['item_num'],
            data['item_name'],
            data['item_price'],
            data['item_size'],
            data['item_storage'],
            data['item_exp']
        ))
        conn.commit()
        return jsonify({"success": True})
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/items', methods=['PUT'])
def add_item():
    data = request.get_json()
    conn = get_db()
    try:
        conn.execute(
            '''INSERT INTO item (item_num, item_name, item_size, item_price, item_exp, item_storage)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (data['item_num'], data['item_name'], data['item_size'], data['item_price'], data['item_exp'], data['item_storage'])
        )
        conn.commit()
        return jsonify({"success": True})
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/items/<item_id>', methods=['DELETE'])
def delete_item(item_id):
    conn = get_db()
    try:
        conn.execute('BEGIN')
        cursor = conn.execute('DELETE FROM item WHERE item_num = ?', (item_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Item not found"}), 404
        return jsonify({"success": True})
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/items', methods=['GET'])
def get_all_items():
    conn = get_db()
    try:
        items = conn.execute('SELECT * FROM item').fetchall()
        return jsonify([dict(item) for item in items])
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/item/<item_num>', methods=['GET'])
def get_item(item_num):
    conn = get_db()
    try:
        item = conn.execute('''
            SELECT i.*, e.event_price
            FROM item i
            LEFT JOIN event e ON i.item_num = e.item_num
            WHERE i.item_num = ?
        ''', (item_num,)).fetchone()
        if item:
            return jsonify(dict(item))
        return jsonify({"error": "Item not found"}), 404
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.json
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO cart (item_num, quantity)
            VALUES (?, ?)
            ON CONFLICT(item_num) DO UPDATE SET quantity = quantity + 1
        ''', (data['item_num'], 1))
        conn.commit()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Invalid item number"}), 400
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/cart', methods=['GET'])
def get_cart():
    conn = get_db()
    try:
        cart_items = conn.execute('''
            SELECT c.item_num, i.item_name, i.item_price,
                   COALESCE(e.event_price, i.item_price) AS final_price,
                   c.quantity
            FROM cart c
            JOIN item i ON c.item_num = i.item_num
            LEFT JOIN event e ON i.item_num = e.item_num
        ''').fetchall()

        items = [dict(item) for item in cart_items]
        total = sum(item['final_price'] * item['quantity'] for item in items)
        discount = sum((item['item_price'] - item['final_price']) * item['quantity'] for item in items)

        return jsonify({
            "items": items,
            "total": total,
            "discount": discount,
            "final_total": total - discount
        })
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/cart/<int:cart_num>', methods=['GET'])
def get_cart_by_num(cart_num):
    conn = get_db()
    try:
        cart_items = conn.execute('''
            SELECT c.cart_num, c.item_num, i.item_name, i.item_price,
                   COALESCE(e.event_price, i.item_price) AS final_price,
                   c.quantity,
                   COALESCE(e.event_price, i.item_price) * c.quantity AS total_price
            FROM cart c
            JOIN item i ON c.item_num = i.item_num
            LEFT JOIN event e ON i.item_num = e.item_num
            WHERE c.cart_num = ?
        ''', (cart_num,)).fetchall()

        if not cart_items:
            return jsonify({"error": "Cart not found"}), 404

        return jsonify([dict(item) for item in cart_items])
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.json
    conn = get_db()
    try:
        item_exists = conn.execute('SELECT 1 FROM item WHERE item_num = ?', (data['item_num'],)).fetchone()
        if not item_exists:
            return jsonify({"success": False, "error": "존재하지 않는 물품번호입니다."}), 400

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
        return jsonify({"success": True})
    except sqlite3.Error as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/events', methods=['GET'])
def get_events():
    conn = get_db()
    try:
        events = conn.execute('''
            SELECT e.*, i.item_name, i.item_price
            FROM event e
            JOIN item i ON e.item_num = i.item_num
        ''').fetchall()
        return jsonify([dict(event) for event in events])
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/events/<item_num>', methods=['DELETE'])
def delete_event(item_num):
    conn = get_db()
    try:
        cursor = conn.execute('DELETE FROM event WHERE item_num = ?', (item_num,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Event not found"}), 404
        return jsonify({"success": True})
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/items/<rfid_number>', methods=['GET'])
def get_item_info(rfid_number):
    item = get_item_info_by_rfid(rfid_number)
    if item:
        return jsonify({
            "item_name": item["item_name"],
            "item_exp": item["item_exp"],
            "item_storage": item["item_storage"]
        })
    else:
        return jsonify({"error": "해당 물품을 찾을 수 없습니다."}), 404

if __name__ == '__main__':
    app.run(debug=True)

