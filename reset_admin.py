import os
from werkzeug.security import generate_password_hash
from db import get_db_connection  # ✅ Import shared DB logic

# Configuration
USERNAME = 'hoody'
NEW_PASSWORD = 'hoodie25'

# Connect using shared function
conn = get_db_connection('admin.db')
cursor = conn.cursor()

# Hash the new password
hashed_password = generate_password_hash(NEW_PASSWORD)

# Check if user exists
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
