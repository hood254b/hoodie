import os
import json
import sqlite3
import asyncio
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from telegram import Bot, Update
from werkzeug.security import generate_password_hash, check_password_hash

from bot import application
from db import get_db_path, get_db_connection

# --- Configuration ---
app = Flask(__name__)
app.secret_key = os.getenv('HOODIE', 'hoodie')
BOT_TOKEN = os.getenv('BOT_TOKEN', 'your-bot-token')
CHAT_ID_FILE = 'chat_ids.txt'
USER_DATA_FILE = 'users.json'
ADMIN_CHAT_ID = "6659858896"
USERNAME = 'hoody'
PASSWORD = 'hoodie25'

bot = Bot(token=BOT_TOKEN)

# --- DB Setup ---
def init_databases():
    schemas = {
        'broadcast_logs.db': '''
            CREATE TABLE IF NOT EXISTS broadcast_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT,
                status TEXT,
                timestamp TEXT,
                message_snippet TEXT
            )
        ''',
        'admin.db': '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        '''
    }
    for name, schema in schemas.items():
        path = get_db_path(name)
        conn = sqlite3.connect(path)
        conn.execute(schema)
        conn.commit()
        conn.close()

def reset_admin_user():
    conn = get_db_connection('admin.db')
    cursor = conn.cursor()
    hashed = generate_password_hash(PASSWORD)
    cursor.execute("SELECT * FROM users WHERE username = ?", (USERNAME,))
    user = cursor.fetchone()

    if user:
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed, USERNAME))
        print(f"[INIT] ✅ Admin user '{USERNAME}' updated.")
    else:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (USERNAME, hashed))
        print(f"[INIT] ✅ Admin user '{USERNAME}' created.")

    conn.commit()
    conn.close()

init_databases()
reset_admin_user()

# --- Async Send ---
async def async_send_message(chat_id, message):
    try:
        await bot.send_message(chat_id=chat_id, text=message)
        return True
    except Exception as e:
        print(f"❌ Failed to send to {chat_id}: {e}")
        return False

async def broadcast_all(chat_ids, message):
    tasks = [async_send_message(chat_id, message) for chat_id in chat_ids]
    return await asyncio.gather(*tasks)

# --- Routes ---
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return 'ok'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection('admin.db')
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            conn.close()

            if user and check_password_hash(user['password'], password):
                session['logged_in'] = True
                session['username'] = username
                return redirect('/dashboard')
        except Exception as e:
            print(f"Login error: {e}")

        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    user_count = 0
    users = {}
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            users = json.load(f)
            user_count = len(users)

    log_count = 0
    try:
        conn = get_db_connection('broadcast_logs.db')
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM broadcast_logs")
        log_count = cur.fetchone()[0]
        conn.close()
    except Exception as e:
        print(f"Error loading log count: {e}")

    return render_template('dashboard.html',
                           user_count=user_count,
                           users=users.values(),
                           log_count=log_count)

@app.route('/broadcast', methods=['POST'])
def broadcast():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    message = request.form['message']
    if not message:
        return "Message cannot be empty", 400

    # Get chat IDs
    chat_ids = []
    if os.path.exists(CHAT_ID_FILE):
        with open(CHAT_ID_FILE, 'r') as f:
            chat_ids = [line.strip() for line in f if line.strip()]

    results = asyncio.run(broadcast_all(chat_ids, message))

    # DB logging
    success_count = 0
    failure_count = 0
    conn = get_db_connection('broadcast_logs.db')
    cursor = conn.cursor()

    for chat_id, result in zip(chat_ids, results):
        status = 'success' if result else 'failure'
        if result:
            success_count += 1
        else:
            failure_count += 1

        cursor.execute('''
            INSERT INTO broadcast_logs (chat_id, status, timestamp, message_snippet)
            VALUES (?, ?, ?, ?)
        ''', (
            chat_id,
            status,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            message[:100]
        ))

    conn.commit()
    conn.close()

    # Notify Admin
    summary = f"""
<b>Broadcast Summary:</b>
✅ Sent: <b>{success_count}</b>
❌ Failed: <b>{failure_count}</b>
"""
    asyncio.run(async_send_message(ADMIN_CHAT_ID, summary))

    return redirect(url_for('dashboard'))

@app.route('/broadcast-history')
def broadcast_history():
    try:
        conn = get_db_connection('broadcast_logs.db')
        logs = conn.execute("SELECT * FROM broadcast_logs ORDER BY timestamp DESC LIMIT 5000").fetchall()
        conn.close()
        return render_template('broadcast_history.html', logs=logs)
    except Exception as e:
        print(f"History error: {e}")
        return "Could not load history", 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True')
