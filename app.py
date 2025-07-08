import json
import os
from dbm import sqlite3

import psycopg2
from flask import Flask, render_template, request, redirect, url_for, session
from sqlalchemy import Update
from telegram import Bot
from werkzeug.security import check_password_hash
import asyncio
from datetime import datetime
from bot import application

app = Flask(__name__)
app.secret_key = 'hood'

BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'
CHAT_ID_FILE = 'chat_ids.txt'
USER_DATA_FILE = 'users.json'
bot = Bot(token=BOT_TOKEN)

USERNAME = 'hoody'
PASSWORD = 'hoodie25'

# === Database setup ===
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# === Init DB: Only needed once ===
def init_logs_table():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS broadcast_logs (
                id SERIAL PRIMARY KEY,
                chat_id TEXT,
                status TEXT,
                timestamp TEXT,
                message_snippet TEXT
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print("Error initializing broadcast_logs table:", e)

init_logs_table()


@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return 'ok'


@app.route('/broadcast-history')
def broadcast_history():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM broadcast_logs ORDER BY timestamp DESC LIMIT 5000')
    rows = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    logs = [dict(zip(colnames, row)) for row in rows]
    conn.close()
    return render_template('broadcast_history.html', logs=logs)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # This part still uses SQLite for user auth, unless you've moved user data to Postgres too
        conn = sqlite3.connect('admin.db')
        conn.row_factory = sqlite3.Row
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

    message = request.form['message']
    success_count = 0
    failure_count = 0

    chat_ids = []
    if os.path.exists(CHAT_ID_FILE):
        with open(CHAT_ID_FILE, 'r') as f:
            chat_ids = [line.strip() for line in f if line.strip()]

    keyboard = [[
        InlineKeyboardButton(
            text="👑 Access VIP (/vip)",
            url="http://t.me/mastermind1X2_bot?start=vip"
        )
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    conn = get_db_connection()
    cur = conn.cursor()

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

        cur.execute('''
            INSERT INTO broadcast_logs (chat_id, status, timestamp, message_snippet)
            VALUES (%s, %s, %s, %s)
        ''', (
            chat_id,
            status,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            message[:100]
        ))

    conn.commit()
    conn.close()

    admin_chat_id = "6659858896"
    summary_msg = f"""
       <b>Broadcast completed:</b>
       ✅ Successfully sent to <b>{success_count}</b> users.
       ❌ Failed to send to <b>{failure_count}</b> users.
    """
    bot.send_message(
        chat_id=admin_chat_id,
        text=summary_msg,
        parse_mode="HTML"
    )

    return f"""
        <h3>📢 Broadcast Completed</h3>
        <p>✅ Successfully sent to <strong>{success_count}</strong> users.</p>
        <p>❌ Failed to send to <strong>{failure_count}</strong> users.</p>
        <br>
        <a href="/dashboard">⬅ Back to Dashboard</a> | 
        <a href="/broadcast-history">📋 View History</a>
    """


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

            asyncio.run(send_all())
            message_status = f"Message sent to {len(ids)} users."

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM broadcast_logs')
    log_count = cur.fetchone()[0]
    conn.close()

    return render_template(
        'dashboard.html',
        user_count=user_count,
        users=users.values(),
        status=message_status,
        log_count=log_count
    )


if __name__ == '__main__':
    app.run(debug=True)
