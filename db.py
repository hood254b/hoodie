# db.py
import sqlite3

DATABASE = 'audience.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def record_audience(chat_id):
    try:
        with get_db_connection() as conn:
            conn.execute('INSERT OR IGNORE INTO audience (chat_id) VALUES (?)', (chat_id,))
            conn.commit()
    except Exception as e:
        print(f"[ERROR] Could not record chat_id {chat_id}: {e}")
