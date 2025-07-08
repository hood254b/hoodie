import datetime
import json
import sqlite3
import os
from threading import Lock
from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import Update
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from werkzeug.security import check_password_hash
import asyncio
from functools import wraps

from bot import application

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database setup
db_lock = Lock()
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'your-bot-token-here')
CHAT_ID_FILE = 'chat_ids.txt'
USER_DATA_FILE = 'users.json'
bot = Bot(token=BOT_TOKEN)

USERNAME = 'hoody'
PASSWORD = 'hoodie25'

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return 'ok'



# Initialize databases
def init_databases():
    with db_lock:
        # Broadcast logs DB
        conn = sqlite3.connect('broadcast_logs.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS broadcast_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id TEXT,
                status TEXT,
                timestamp TEXT,
                message_snippet TEXT,
                full_message TEXT
            )
        ''')
        conn.commit()
        conn.close()

        # Admin DB
        conn = sqlite3.connect('admin.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        conn.commit()
        conn.close()


init_databases()


# Async support for Flask routes
def async_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(f(*args, **kwargs))
        finally:
            loop.close()
        return result

    return wrapper


# Helper functions
def get_db_connection(db_name):
    conn = sqlite3.connect(db_name)
    conn.row_factory = sqlite3.Row
    return conn


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# Routes
@app.route('/')
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection('admin.db')
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))

        return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    # Get user count
    user_count = 0
    if os.path.exists(CHAT_ID_FILE):
        with open(CHAT_ID_FILE, 'r') as f:
            user_count = len(f.readlines())

    # Get log count
    log_count = 0
    conn = get_db_connection('broadcast_logs.db')
    log_count = conn.execute('SELECT COUNT(*) FROM broadcast_logs').fetchone()[0]
    conn.close()

    return render_template(
        'dashboard.html',
        user_count=user_count,
        log_count=log_count
    )


@app.route('/broadcast', methods=['GET', 'POST'])
@login_required
@async_route
async def broadcast():
    if request.method == 'GET':
        return render_template('broadcast.html')

    message = request.form['message']
    chat_ids = []

    if os.path.exists(CHAT_ID_FILE):
        with open(CHAT_ID_FILE, 'r') as f:
            chat_ids = [line.strip() for line in f if line.strip()]

    keyboard = [[InlineKeyboardButton(text="👑 VIP Access", url="http://t.me/mastermind1X2_bot?start=vip")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    success_count = 0
    failure_count = 0

    conn = get_db_connection('broadcast_logs.db')
    cursor = conn.cursor()

    for chat_id in chat_ids:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            status = 'success'
            success_count += 1
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")
            status = 'failure'
            failure_count += 1

        cursor.execute('''
            INSERT INTO broadcast_logs 
            (chat_id, status, timestamp, message_snippet, full_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            chat_id,
            status,
            datetime.datetime.now().isoformat(),
            message[:100],
            message
        ))
        conn.commit()

    conn.close()

    # Send summary to admin
    try:
        await bot.send_message(
            chat_id="6659858896",
            text=f"""
            <b>📢 Broadcast Summary</b>
            ✅ Success: {success_count}
            ❌ Failed: {failure_count}
            📅 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
            """,
            parse_mode='HTML'
        )
    except Exception as e:
        print(f"Failed to send summary: {e}")

    return redirect(url_for('broadcast_history'))


@app.route('/broadcast-history')
@login_required
def broadcast_history():
    conn = get_db_connection('broadcast_logs.db')
    logs = conn.execute('''
        SELECT * FROM broadcast_logs 
        ORDER BY timestamp DESC 
        LIMIT 100
    ''').fetchall()
    conn.close()

    return render_template('broadcast_history.html', logs=logs)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)