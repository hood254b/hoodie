import sqlite3
from werkzeug.security import generate_password_hash
from db import get_db_path  # Use the shared path logic from db.py

# Configuration
USERNAME = 'hoody'
NEW_PASSWORD = 'hoodie25'

# Resolve correct DB path
db_path = get_db_path('admin.db')

# Connect and update user
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create users table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
''')

# Hash the new password
hashed_password = generate_password_hash(NEW_PASSWORD)

# Check if user exists
cursor.execute("SELECT * FROM users WHERE username = ?", (USERNAME,))
existing_user = cursor.fetchone()

# Update or insert admin user
if existing_user:
    cursor.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (hashed_password, USERNAME)
    )
    print(f"✅ Admin user '{USERNAME}' has been reset successfully.")
else:
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (USERNAME, hashed_password)
    )
    print(f"✅ Admin user '{USERNAME}' has been created.")

conn.commit()
conn.close()
