import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect('admin.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')

username = 'hoody'
password = 'hoodie25'
hashed = generate_password_hash(password)

try:
    conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
    print("✅ Admin user created.")
except sqlite3.IntegrityError:
    print("⚠️ Admin user already exists.")

conn.commit()
conn.close()
