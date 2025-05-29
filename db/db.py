{\rtf1\ansi\ansicpg949\cocoartf2818
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\fnil\fcharset129 AppleSDGothicNeo-Regular;\f2\fnil\fcharset0 AppleColorEmoji;
}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww28600\viewh14700\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import sqlite3\
\
# 
\f1 \'b5\'a5\'c0\'cc\'c5\'cd\'ba\'a3\'c0\'cc\'bd\'ba
\f0  
\f1 \'c6\'c4\'c0\'cf
\f0  
\f1 \'b0\'e6\'b7\'ce
\f0  
\f1 \'bc\'b3\'c1\'a4
\f0 \
# 
\f1 \'c7\'ca\'bf\'e4\'bf\'a1
\f0  
\f1 \'b5\'fb\'b6\'f3
\f0  
\f1 \'b0\'e6\'b7\'ce\'b8\'a6
\f0  
\f1 \'c8\'af\'b0\'e6
\f0  
\f1 \'ba\'af\'bc\'f6\'b3\'aa
\f0  
\f1 \'bc\'b3\'c1\'a4
\f0  
\f1 \'c6\'c4\'c0\'cf\'b7\'ce
\f0  
\f1 \'ba\'d0\'b8\'ae\'c7\'d2
\f0  
\f1 \'bc\'f6
\f0  
\f1 \'c0\'d6\'bd\'c0\'b4\'cf\'b4\'d9
\f0 .\
DATABASE = r'C:\\Users\\911\\Downloads\\smart_cart-main\\smart_cart-main\\db\\capstone.sqlite3'\
\
def get_db():\
    """\
    SQLite 
\f1 \'b5\'a5\'c0\'cc\'c5\'cd\'ba\'a3\'c0\'cc\'bd\'ba\'bf\'a1
\f0  
\f1 \'bf\'ac\'b0\'e1\'c7\'cf\'b4\'c2
\f0  
\f1 \'c7\'d4\'bc\'f6
\f0 \
    """\
    conn = sqlite3.connect(DATABASE)\
    conn.row_factory = sqlite3.Row\
    return conn\
\
def enable_foreign_keys():\
    """\
    SQLite 
\f1 \'bf\'dc\'b7\'a1
\f0  
\f1 \'c5\'b0
\f0  
\f1 \'c8\'b0\'bc\'ba\'c8\'ad
\f0 \
    """\
    conn = get_db()\
    conn.execute('PRAGMA foreign_keys = ON')\
    conn.commit()\
    conn.close()\
\
def add_to_cart_by_uid(uid, cart_num=1):\
    """\
    RFID UID
\f1 \'b8\'a6
\f0  
\f1 \'bb\'e7\'bf\'eb\'c7\'cf\'bf\'a9
\f0  
\f1 \'c4\'ab\'c6\'ae\'bf\'a1
\f0  
\f1 \'b9\'b0\'c7\'b0
\f0  
\f1 \'c3\'df\'b0\'a1
\f0 \
    """\
    print(f"
\f2 \uc0\u55357 \u57042 
\f0  UID \{uid\}
\f1 \'b8\'a6
\f0  DB
\f1 \'bf\'a1
\f0  
\f1 \'c3\'df\'b0\'a1
\f0  
\f1 \'c1\'df
\f0 ...")\
    conn = get_db()\
    try:\
        conn.execute(''' \
            INSERT INTO cart (cart_num, item_num, quantity) \
            VALUES (?, ?, 1)\
            ON CONFLICT(cart_num, item_num) DO UPDATE SET quantity = quantity + 1\
        ''', (cart_num, uid))\
        conn.commit()\
        print(f"[DB] UID \{uid\} 
\f1 \'c4\'ab\'c6\'ae\'bf\'a1
\f0  
\f1 \'c3\'df\'b0\'a1
\f0  
\f1 \'bf\'cf\'b7\'e1
\f0 ")\
    except sqlite3.Error as e:\
        print(f"[DB 
\f1 \'bf\'c0\'b7\'f9
\f0 ] \{e\}")\
    finally:\
        conn.close()\
\
def get_item_info_by_rfid(rfid_number):\
    """\
    RFID 
\f1 \'b9\'f8\'c8\'a3\'b7\'ce
\f0  
\f1 \'b9\'b0\'c7\'b0
\f0  
\f1 \'c1\'a4\'ba\'b8\'b8\'a6
\f0  
\f1 \'c1\'b6\'c8\'b8
\f0 \
    """\
    conn = get_db()\
    item = conn.execute('''\
        SELECT item_name, item_exp, item_storage\
        FROM item\
        WHERE item_num = ?\
    ''', (rfid_number,)).fetchone()\
    conn.close()\
    return item\
}