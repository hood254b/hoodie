DATABASE_URI = 'sqlite:///users.db'
# config.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'users.db')}"

BOT_TOKEN = '7270921648:AAH4qX80XtgKUoCzbMlNsDec6enm4TWNKR4'
ADMIN_USERNAME = 'hood'  # For login
ADMIN_PASSWORD = '#hood111'  # Use hashed password in production