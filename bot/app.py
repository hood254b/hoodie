from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from telegram import Bot
import sqlite3
from werkzeug.security import check_password_hash

import asyncio
app = Flask(__name__)
app.secret_key = 'hood'

BOT_TOKEN = '7270921648:AAH4qX80XtgKUoCzbMlNsDec6enm4TWNKR4'
CHAT_ID_FILE = 'chat_ids.txt'
USER_DATA_FILE = 'users.json'
bot = Bot(token=BOT_TOKEN)


USERNAME = 'hoody'
PASSWORD = 'hoodie25'

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

