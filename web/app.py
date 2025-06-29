from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'db')))
from database import get_db, enable_foreign_keys, add_or_update_event, get_item_info_by_rfid, remove_from_cart_by_uid

app = Flask(__name__)
DATABASE = r'/home/rpi4/Desktop/smart_cart/db/capstone.sqlite3'
#DATABASE = r'C:\Users\chu\Desktop\smart_cart-1\db\capstone.sqlite3'

@app.route('/')
def index():
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

# ✅ 장바구니 삭제 API 추가 (결제 시 사용)
@app.route('/api/cart/<int:cart_num>', methods=['DELETE'])
def clear_cart(cart_num):
    conn = get_db()
    try:
        cursor = conn.execute('DELETE FROM cart WHERE cart_num = ?', (cart_num,))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "해당 카트에 항목이 없습니다."}), 404
        return jsonify({"success": True})
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.json
    success, error_message = add_or_update_event(data)
    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "error": error_message}), 400

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
