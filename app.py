import json
import sqlite3

import os

from flask import Flask, render_template, request, redirect, url_for, session


def init_logs_db():
    conn = sqlite3.connect('broadcast_logs.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS broadcast_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            status TEXT,
            timestamp TEXT,
            message_snippet TEXT
        )
    ''')
    conn.commit()
    conn.close()


init_logs_db()

from sqlalchemy import Update
from telegram import Bot
from werkzeug.security import check_password_hash

import asyncio

from bot import application

app = Flask(__name__)
app.secret_key = 'hood'

BOT_TOKEN = '7270921648:AAH4qX80XtgKUoCzbMlNsDec6enm4TWNKR4'
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


@app.route('/broadcast-history')
def broadcast_history():
    conn = sqlite3.connect('broadcast_logs.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM broadcast_logs ORDER BY timestamp DESC LIMIT 5000')
    logs = cursor.fetchall()
    conn.close()
    return render_template('broadcast_history.html', logs=logs)

@app.route('/broadcast-history')
def view_broadcast_history():
    conn = sqlite3.connect('broadcast_logs.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM broadcast_logs ORDER BY timestamp DESC LIMIT 5000')
    logs = cursor.fetchall()
    conn.close()
    return render_template('broadcast_history.html', logs=logs)




def get_db_connection():
    conn = sqlite3.connect('admin.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')


@app.route('/broadcast', methods=['POST'])
def broadcast():
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from datetime import datetime
    import sqlite3

    message = request.form['message']
    success_count = 0
    failure_count = 0

    chat_ids = []
    if os.path.exists(CHAT_ID_FILE):
        with open(CHAT_ID_FILE, 'r') as f:
            chat_ids = [line.strip() for line in f if line.strip()]

    # VIP link button
    keyboard = [[
        InlineKeyboardButton(
            text="👑 Access VIP (/vip)",
            url="http://t.me/mastermind1X2_bot?start=vip"
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 🟢 BEGIN: Insert broadcast logs
    conn = sqlite3.connect('broadcast_logs.db')
    cursor = conn.cursor()

    for chat_id in chat_ids:
        try:
            bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=reply_markup
            )
            status = 'success'
            success_count += 1
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")
            status = 'failure'
            failure_count += 1

        # Save to DB
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
    # 🔴 END

    # Optional: Display result page
    return render_template("broadcast_result.html", success=success_count, failure=failure_count)



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    message_status = ""
    user_count = 0
    users = {}

    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            users = json.load(f)
            user_count = len(users)

    if request.method == 'POST':
        message = request.form['message']
        if os.path.exists(CHAT_ID_FILE):
            with open(CHAT_ID_FILE, 'r') as f:
                ids = set(f.read().splitlines())

            async def send_all():
                for chat_id in ids:
                    try:
                        await bot.send_message(chat_id=chat_id, text=message)
                    except Exception as e:
                        print(f"Failed to send to {chat_id}: {e}")

            asyncio.run(send_all())  # Only run the loop once
            message_status = f"Message sent to {len(ids)} users."

    return render_template('dashboard.html', user_count=user_count, users=users.values(), status=message_status)



if __name__ == '__main__':
    app.run(debug=True)

