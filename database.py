import sqlite3

conn = sqlite3.connect("shop.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    total_purchases INTEGER DEFAULT 0
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    price INTEGER,
    description TEXT,
    file_path TEXT
)''')

conn.commit()

def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone()

def create_user(user_id):
    cursor.execute("INSERT INTO users(user_id) VALUES(?)", (user_id,))
    conn.commit()

def add_balance(user_id, amount):
    cursor.execute("UPDATE users SET balance = balance + ?, total_purchases = total_purchases + 1 WHERE user_id=?", (amount, user_id))
    conn.commit()

def get_items():
    cursor.execute("SELECT id, price, description FROM items")
    return cursor.fetchall()

def get_item(item_id):
    cursor.execute("SELECT id, price, description, file_path FROM items WHERE id=?", (item_id,))
    return cursor.fetchone()
