import sqlite3
import os

def get_db_path(db_name):
    if 'RENDER' in os.environ:
        base_dir = '/tmp/db'
        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, db_name)
    return db_name

def get_db_connection(db_name):
    db_path = get_db_path(db_name)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
