import json
import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import Update
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from werkzeug.security import check_password_hash
import asyncio
from bot import application
from db import get_db_path, get_db_connection



# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('HOODIE', 'hoodie')  # Change for production

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', '7270921648:AAH4qX80XtgKUoCzbMlNsDec6enm4TWNKR4')
CHAT_ID_FILE = 'chat_ids.txt'
USER_DATA_FILE = 'users.json'
ADMIN_CHAT_ID = "6659858896"  # Your admin chat ID
USERNAME = 'hoody'
PASSWORD = 'hoodie25'


def init_databases():
    """Initialize all required databases"""
    databases = {
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

    for db_name, schema in databases.items():
        db_path = get_db_path(db_name)
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute(schema)
        conn.commit()
        conn.close()


init_databases()
from werkzeug.security import generate_password_hash

def reset_admin_user():
    db_conn = get_db_connection('admin.db')
    cursor = db_conn.cursor()

    hashed_password = generate_password_hash(PASSWORD)

    cursor.execute("SELECT * FROM users WHERE username = ?", (USERNAME,))
    user = cursor.fetchone()

    if user:
        cursor.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, USERNAME))
        print(f"[INIT] ✅ Admin user '{USERNAME}' password reset.")
    else:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (USERNAME, hashed_password))
        print(f"[INIT] ✅ Admin user '{USERNAME}' created.")

    db_conn.commit()
    db_conn.close()

# Call it
reset_admin_user()


# Telegram Bot
bot = Bot(token=BOT_TOKEN)


async def async_send_message(chat_id, message, reply_markup=None):
    """Wrapper for an async message sending"""
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=message,
            reply_markup=reply_markup
        )
        return True
    except Exception as e:
        print(f"Failed to send to {chat_id}: {e}")
        return False


# Routes
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return 'ok'


@app.route('/broadcast-history')
def broadcast_history():
    try:
        conn = get_db_connection('broadcast_logs.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM broadcast_logs ORDER BY timestamp DESC LIMIT 5000')
        logs = cursor.fetchall()
        conn.close()
        return render_template('broadcast_history.html', logs=logs)
    except Exception as e:
        print(f"Error accessing broadcast history: {e}")
        return "Error loading broadcast history", 500


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            conn = get_db_connection('admin.db')
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            conn.close()

            if user and check_password_hash(user['password'], password):
                session['logged_in'] = True
                session['username'] = username
                return redirect('/dashboard')
        except Exception as e:
            print(f"Login error: {e}")

        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/broadcast', methods=['POST'])
def broadcast():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    message = request.form['message']
    if not message:
        return "Message cannot be empty", 400

    # Prepare VIP button
    keyboard = [[InlineKeyboardButton(
        text="👑 Access VIP (/vip)",
        url="http://t.me/mastermind1X2_bot?start=vip"
    )]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Get chat IDs
    chat_ids = []
    if os.path.exists(CHAT_ID_FILE):
        with open(CHAT_ID_FILE, 'r') as f:
            chat_ids = [line.strip() for line in f if line.strip()]

    # Initialize counters and DB
    success_count = 0
    failure_count = 0
    db_conn = get_db_connection('broadcast_logs.db')
    db_cursor = db_conn.cursor()

    # Process broadcasts
    for chat_id in chat_ids:
        try:
            # Send a message (async)
            success = asyncio.run(async_send_message(
                chat_id=chat_id,
                message=message,
                reply_markup=reply_markup
            ))

            # Update counters and log
            if success:
                success_count += 1
                status = 'success'
            else:
                failure_count += 1
                status = 'failure'

            db_cursor.execute('''
                INSERT INTO broadcast_logs (chat_id, status, timestamp, message_snippet)
                VALUES (?, ?, ?, ?)
            ''', (
                chat_id,
                status,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                message[:100]
            ))

        except Exception as e:
            print(f"Error processing chat_id {chat_id}: {e}")
            failure_count += 1

    # Finalize DB operations
    db_conn.commit()
    db_conn.close()

    # Send admin notification
    summary_msg = f"""
        <b>Broadcast completed:</b>
        ✅ Successfully sent to <b>{success_count}</b> users.
        ❌ Failed to send to <b>{failure_count}</b> users.
    """
    asyncio.run(async_send_message(
        chat_id=ADMIN_CHAT_ID,
        message=summary_msg,
    ))

    return redirect(url_for('dashboard'))


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    # Get user count
    user_count = 0
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            users = json.load(f)
            user_count = len(users)

    # Get log count
    log_count = 0
    try:
        conn = get_db_connection('broadcast_logs.db')
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) FROM broadcast_logs')
        log_count = cur.fetchone()[0]
        conn.close()
    except Exception as e:
        print(f"Error getting log count: {e}")

    return render_template(
        'dashboard.html',
        user_count=user_count,
        users=users.values() if 'users' in locals() else [],
        log_count=log_count
    )


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False') == 'True')