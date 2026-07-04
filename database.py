import sqlite3
from datetime import datetime

DB_NAME = "orders.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        customer_name TEXT,
        customer_username TEXT,
        status TEXT DEFAULT 'new',
        created_at TEXT,
        updated_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS order_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        sender TEXT NOT NULL,
        message_type TEXT NOT NULL,
        content TEXT,
        telegram_file_id TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS information_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        driver_request TEXT,
        customer_response TEXT,
        created_at TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS completions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        message TEXT,
        file_id TEXT,
        file_type TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def create_order(customer_id, customer_name, customer_username):
    conn = get_connection()
    cur = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO orders (
            customer_id,
            customer_name,
            customer_username,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        customer_id,
        customer_name,
        customer_username,
        "new",
        now,
        now
    ))

    order_id = cur.lastrowid

    conn.commit()
    conn.close()

    return order_id


def save_order_message(
    order_id,
    sender,
    message_type,
    content=None,
    telegram_file_id=None
):
    conn = get_connection()
    cur = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO order_messages(
            order_id,
            sender,
            message_type,
            content,
            telegram_file_id,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        order_id,
        sender,
        message_type,
        content,
        telegram_file_id,
        now
    ))

    conn.commit()
    conn.close()


def update_order_status(order_id, status):
    conn = get_connection()
    cur = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        UPDATE orders
        SET status = ?, updated_at = ?
        WHERE id = ?
    """, (
        status,
        now,
        order_id
    ))

    conn.commit()
    conn.close()


def get_order(order_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM orders
        WHERE id = ?
    """, (order_id,))

    order = cur.fetchone()

    conn.close()

    return order


def get_active_orders():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM orders
        WHERE status = 'active'
        ORDER BY created_at ASC
    """)

    orders = cur.fetchall()

    conn.close()

    return orders


def save_information_request(order_id, driver_request):
    conn = get_connection()
    cur = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO information_requests(
            order_id,
            driver_request,
            created_at
        )
        VALUES (?, ?, ?)
    """, (
        order_id,
        driver_request,
        now
    ))

    conn.commit()
    conn.close()


def save_customer_response(order_id, response):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE information_requests
        SET customer_response = ?
        WHERE order_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (
        response,
        order_id
    ))

    conn.commit()
    conn.close()


def save_completion(
    order_id,
    message=None,
    file_id=None,
    file_type=None
):
    conn = get_connection()
    cur = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO completions(
            order_id,
            message,
            file_id,
            file_type,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        order_id,
        message,
        file_id,
        file_type,
        now
    ))

    conn.commit()
    conn.close()
