import os
import sqlite3
from werkzeug.security import generate_password_hash

# Configuration
USERNAME = 'hoody'
NEW_PASSWORD = 'hoodie25'

# Safe path logic
def get_db_path(db_name):
    if 'RENDER' in os.environ:
        return os.path.join('/tmp/db', db_name)
    return db_name

db_path = get_db_path('admin.db')

# Ensure the directory exists (useful for RENDER.com)
if 'RENDER' in os.environ:
    os.makedirs('/tmp/db', exist_ok=True)

# Connect and update user
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

hashed_password = generate_password_hash(NEW_PASSWORD)

cursor.execute("SELECT * FROM users WHERE username = ?", (USERNAME,))
existing_user = cursor.fetchone()

if existing_user:
    cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, USERNAME))
    print(f"✅ Admin user '{USERNAME}' has been reset successfully.")
else:
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (USERNAME, hashed_password))
    print(f"✅ Admin user '{USERNAME}' has been created.")

conn.commit()
conn.close()
