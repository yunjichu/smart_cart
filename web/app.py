from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import threading
import serial
import time

app = Flask(__name__)
DATABASE = r'/home/rpi4/Desktop/smart_cart/db/capstone.sqlite3'

def get_db():
    """
    SQLite 데이터베이스에 연결하는 함수
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.before_request
def enable_foreign_keys():
    """
    요청 전에 SQLite에서 외래 키를 활성화
    """
    conn = get_db()
    conn.execute('PRAGMA foreign_keys = ON')
    conn.commit()
    conn.close()

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
    """
    물품 등록 페이지
    """
    return render_template('items.html')

@app.route('/events', methods=['GET'])
def events_page():
    """
    할인 행사 페이지
    """
    return render_template('events.html')

@app.route('/transactions', methods=['GET'])
def transactions_page():
    """
    거래 내역 페이지
    """
    return render_template('transactions.html')

@app.route('/api/items', methods=['POST'])
def register_item():
    """
    물품 등록 API
    """
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
    """
    물품 추가 API
    """
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
    """
    물품 삭제 API
    """
    conn = get_db()
    try:
        # 트랜잭션 시작
        conn.execute('BEGIN')
        cursor = conn.execute('DELETE FROM item WHERE item_num = ?', (item_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Item not found"}), 404

        return jsonify({"success": True})
    except sqlite3.Error as e:
        conn.rollback()  # 오류 발생 시 롤백
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/items', methods=['GET'])
def get_all_items():
    """
    모든 상품 조회 API
    """
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
    """
    제품 정보 조회 API (RFID 태그 기반)
    """
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
    """
    장바구니 추가 API
    """
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
    """
    장바구니 조회 API
    """
    conn = get_db()
    try:
        cart_items = conn.execute('''
            SELECT c.item_num, i.item_name, i.item_price,
            COALESCE(e.event_price, i.item_price) as final_price,
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
    """
    특정 카트 번호로 장바구니 조회
    """
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


        
# 할인 등록 API
@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.json
    conn = get_db()
    try:
        # 먼저 item_num이 실제 존재하는지 확인
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



# 할인 목록 조회
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

# 할인 삭제 API
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

def add_to_cart1(uid):
    print(f"🛒 UID {uid}를 DB에 추가 중...")
    """카트에 UID 추가하는 함수"""
    conn = get_db()
    try:
        conn.execute(''' 
            INSERT INTO cart (cart_num, item_num, quantity) 
            VALUES (?, ?, 1)
            ON CONFLICT(cart_num, item_num) DO UPDATE SET quantity = quantity + 1
        ''', (1, uid))  # cart_num = 1로 고정, uid는 RFID UID
        conn.commit()
        print(f"[DB] UID {uid} 카트에 추가 완료")
    except sqlite3.Error as e:
        print(f"[DB 오류] {e}")
    finally:
        conn.close()


if __name__ == '__main__':

    # Flask 서버 실행
    app.run(debug=True)

