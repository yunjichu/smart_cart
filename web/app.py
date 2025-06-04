# app.py

from flask import Flask, render_template, request, jsonify
from db.database import get_db, enable_foreign_keys, add_to_cart_by_uid, get_item_info_by_rfid

app = Flask(__name__)

@app.before_request
def before_request():
    enable_foreign_keys()

@app.route('/')
def index():
    total = 10000
    discount = 2000
    return render_template('main.html', total=total, discount=discount)

@app.route('/items')
def items_page():
    return render_template('items.html')

@app.route('/events')
def events_page():
    return render_template('events.html')

@app.route('/transactions')
def transactions_page():
    return render_template('transactions.html')

# --- 상품 API ---

@app.route('/api/items', methods=['POST'])
def register_item():
    data = request.json
    conn = get_db()
    try:
        conn.execute(''' 
            INSERT INTO item (item_num, item_name, item_price, item_size, item_storage, item_exp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['item_num'], data['item_name'], data['item_price'],
            data['item_size'], data['item_storage'], data['item_exp']
        ))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/items', methods=['GET'])
def get_all_items():
    conn = get_db()
    try:
        items = conn.execute('SELECT * FROM item').fetchall()
        return jsonify([dict(item) for item in items])
    except Exception as e:
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
    except Exception as e:
        conn.rollback()
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# --- 카트 API ---

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
    except Exception as e:
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
    except Exception as e:
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/cart/add_uid', methods=['POST'])
def add_uid_to_cart():
    data = request.json
    uid = data.get("uid")
    if not uid:
        return jsonify({"error": "UID가 필요합니다."}), 400
    add_to_cart_by_uid(uid)
    return jsonify({"success": True})

# --- 이벤트 API ---

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
            data['item_num'], origin_price, event_price, event_rate, period,
            origin_price, event_price, event_rate, period
        ))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return
