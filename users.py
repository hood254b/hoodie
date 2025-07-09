import sqlite3
import os

def get_db_path(db_name='admin.db'):
    if 'RENDER' in os.environ:
        return '/tmp/db/admin.db'
    return db_name

conn = sqlite3.connect(get_db_path())
cursor = conn.cursor()

cursor.execute("SELECT id, username, password FROM users")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()
