from cmath import e
from typing import final
from urllib import request

import telegram
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, \
    ConversationHandler, ContextTypes, \
    Application, CallbackContext
from datetime import datetime, time
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import os
import sqlite3

TOKEN: final = '7270921648:AAH4qX80XtgKUoCzbMlNsDec6enm4TWNKR4'
BOT_USERNAME: final = '@mastermind1X2_bot'
ADMIN_ID = 7270921648
CHAT_ID_FILE = "chat_ids.txt"

USER_DATA_FILE = "users.json"
CHAT_ID_FILE = "chat_ids.txt"
BOT_TOKEN = os.environ.get("7270921648:AAH4qX80XtgKUoCzbMlNsDec6enm4TWNKR4")
RENDER_URL = "https://mastermind-j7f9.onrender.com"

# Set up Flask and telegram app
flask_app = Flask(__name__)
application = Application.builder().token(TOKEN).build()



# Route to receive Telegram webhook updates
@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

# Route to manually set webhook
@flask_app.route("/set_webhook")
def set_webhook():
    success = application.bot.set_webhook(f"{RENDER_URL}/webhook")
    return "Webhook set!" if success else "Failed to set webhook."

def save_user_data(user):
    data = {}
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            data = json.load(f)

    user_id = str(user.id)
    data[user_id] = {
        "username": user.username,
        "first_name": user.first_name,
        "address": user.language_code      }

    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f)

    # Save chat_id
    with open(CHAT_ID_FILE, 'a') as f:
        f.write(f"{user.id}\n")





async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    save_user_data(user)
    await update.message.reply_text(
        'Hello ,first of all welcome to the most profitable Betting advisory company with daily winning matches., Be assured of maximum returns from our daily matches.\n\nHere are your free tips for today(/tips)')



async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        await update.message.reply_text('unauthorized')
        return

    message = ''.join(context.args)
    if not message:
        await update.message.reply_text('Please enter a message')
        return

    sent, failed = 0, 0
    if os.path.exists(CHAT_ID_FILE):
        with open(CHAT_ID_FILE, 'r') as f:
            chat_ids = [int(line.strip()) for line in f]

            for chat_id in chat_ids:
                try:
                    context.bot.send_message(chat_id, text=message)
                    sent += 1
                except Exception as e:
                    failed += 1

    await update.message.reply_text(f' broadcast complete.\n messages sent:{sent}\n failed: {failed})')


async def vip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("3-10 VIP ODDS", callback_data='3-10vipodds')],
        [InlineKeyboardButton("10+ VIP ODDS", callback_data='10+vipodds')],
        [InlineKeyboardButton("HT/FT", callback_data='ht/ft')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('<b>Now choose an subscription plan:</b>', parse_mode='HTML', reply_markup=reply_markup)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global reply_markup
    query = update.callback_query
    await query.answer()
    if query.data == '3-10vipodds':
        sub_keyboard = [
            [InlineKeyboardButton('Pay with Cryptocurrency',callback_data='paywithcryptocurrency1')],
            [InlineKeyboardButton('United states', callback_data='unitedstates1')],
            [InlineKeyboardButton('West African CFA Franc BCEAO', callback_data='westafricancfafrancbceao1')],
            [InlineKeyboardButton('CANADA', callback_data='canada1')],
            [InlineKeyboardButton('United Kingdom', callback_data='Unitedkingdom1')],
            [InlineKeyboardButton('European Economic Area', callback_data='europeaneconomicarea1')],
            [InlineKeyboardButton('NIGERIA', callback_data='nigeria1')],
            [InlineKeyboardButton('KENYA', callback_data='kenya1')],
            [InlineKeyboardButton('SOUTH AFRICA', callback_data='southafrica')],
            [InlineKeyboardButton('UGANDA', callback_data='uganda1')],
            [InlineKeyboardButton('GHANA', callback_data='ghana1')],
            [InlineKeyboardButton('TANZANIA', callback_data='tanzania1')],
            [InlineKeyboardButton('MOROCCO', callback_data='morocco1')],
            [InlineKeyboardButton('RWANDA', callback_data='rwanda1')],
            [InlineKeyboardButton('ZAMBIA', callback_data='zambia1')],
            [InlineKeyboardButton('MALAWI', callback_data='malawi1')],
        ]
        reply_markup = InlineKeyboardMarkup(sub_keyboard)
        await query.edit_message_text(text='select country to subscribe for:\n👉 3-10 VIP ODDS',
                                      reply_markup=reply_markup)
    elif query.data == '10+vipodds':
        sub_keyboard = [
            [InlineKeyboardButton('Pay with Cryptocurrency', callback_data='paywithcryptocurrency2')],
            [InlineKeyboardButton('United states', callback_data='unitedstates2')],
            [InlineKeyboardButton('West African CFA Franc BCEAO', callback_data='westafricancfafrancbceao2')],
            [InlineKeyboardButton('CANADA', callback_data='canada2')],
            [InlineKeyboardButton('United Kingdom', callback_data='Unitedkingdom2')],
            [InlineKeyboardButton('European Economic Area', callback_data='europeaneconomicarea2')],
            [InlineKeyboardButton('NIGERIA', callback_data='nigeria2')],
            [InlineKeyboardButton('KENYA', callback_data='kenya2')],
            [InlineKeyboardButton('SOUTH AFRICA', callback_data='southafrica2')],
            [InlineKeyboardButton('UGANDA', callback_data='uganda2')],
            [InlineKeyboardButton('GHANA', callback_data='ghana2')],
            [InlineKeyboardButton('TANZANIA', callback_data='tanzania2')],
            [InlineKeyboardButton('MOROCCO', callback_data='morocco2')],
            [InlineKeyboardButton('RWANDA', callback_data='rwanda2')],
            [InlineKeyboardButton('ZAMBIA', callback_data='zambia2')],
            [InlineKeyboardButton('MALAWI', callback_data='malawi2')],
        ]
        reply_markup = InlineKeyboardMarkup(sub_keyboard)
        await query.edit_message_text(text='select country to subscribe for:\n👉 10+ VIP ODDS',reply_markup=reply_markup)
    elif query.data == 'ht/ft':
        sub_keyboard = [
            [InlineKeyboardButton('Pay with Cryptocurrency', callback_data='paywithcryptocurrency3')],
            [InlineKeyboardButton('United states', callback_data='unitedstates3')],
            [InlineKeyboardButton('West African CFA Franc BCEAO', callback_data='westafricancfafrancbceao3')],
            [InlineKeyboardButton('CANADA', callback_data='canada3')],
            [InlineKeyboardButton('United Kingdom', callback_data='unitedkingdom3')],
            [InlineKeyboardButton('European Economic Area', callback_data='europeaneconomicarea3')],
            [InlineKeyboardButton('NIGERIA', callback_data='nigeria3')],
            [InlineKeyboardButton('KENYA', callback_data='kenya3')],
            [InlineKeyboardButton('SOUTH AFRICA', callback_data='southafrica3')],
            [InlineKeyboardButton('UGANDA', callback_data='uganda3')],
            [InlineKeyboardButton('GHANA', callback_data='ghana3')],
            [InlineKeyboardButton('TANZANIA', callback_data='tanzania3')],
            [InlineKeyboardButton('MOROCCO', callback_data='morocco3')],
            [InlineKeyboardButton('RWANDA', callback_data='rwanda3')],
            [InlineKeyboardButton('ZAMBIA', callback_data='zambia3')],
            [InlineKeyboardButton('MALAWI', callback_data='malawi3')],
        ]
        reply_markup = InlineKeyboardMarkup(sub_keyboard)
        await query.edit_message_text(text='select country to subscribe for:\n👉 HT/FT VIP ODDS', reply_markup=reply_markup)

    elif query.data == 'tanzania1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay TZS: 50,000')
    elif query.data == 'nigeria1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay NGN: 25,000')
    elif query.data == 'paywithcryptocurrency1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='binance.jpg',
            caption="<b>Copy your preferred address to make a monthly subscription of $20 for 3-10 odds \n- Binance ID: 797057741\n- TRC20 Address: TDwiXoR9N1U1WVmLKyC9NPAG6ceYfzJjXc\n-Bit coin Address: 1AGcSgoYB429QHDCT1Z5EkgJoE54QgmWJk\n\nThen send payment screenshot here: contact 👉@mastermindx0</b>", parse_mode='HTML')

    elif query.data == 'kenya1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay KSH: 1,500')
    elif query.data == 'rwanda1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay RWF: 30,000')
    elif query.data == 'unitedstates1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay USD:20')
    elif query.data == 'europeaneconomicarea1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay EUR:25')
    elif query.data == 'uganda1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay UGX: 50,000')
    elif query.data == 'westafricancfafrancbceao1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay CFA: 10,000')
    elif query.data == 'canada1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay CAD: 30')
    elif query.data == 'Unitedkingdom1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay GBP: 15')
    elif query.data == 'southafrica':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay R: 350')
    elif query.data == 'ghana1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay GHC: 250')
    elif query.data == 'morocco1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay MAD: 180')
    elif query.data == 'zambia1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay ZNW: 500')
    elif query.data == 'malawi1':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay MWK: 35,000')

    elif query.data == 'tanzania2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay TZS: 70,000')
    elif query.data == 'nigeria2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay NGN: 40,000')
    elif query.data == 'paywithcryptocurrency2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='binance.jpg',
            caption="<b>Copy your preferred address to make a monthly subscription of $30 for 10+ odds \n- Binance ID: 797057741\n- TRC20 Address: TDwiXoR9N1U1WVmLKyC9NPAG6ceYfzJjXc\n-Bit coin Address: 1AGcSgoYB429QHDCT1Z5EkgJoE54QgmWJk\n\nThen send payment screenshot here: contact 👉@mastermindx0</b>",parse_mode='HTML')
    elif query.data == 'kenya2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay KSH: 3,000')
    elif query.data == 'rwanda2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay RWF: 40,000')
    elif query.data == 'unitedstates2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay USD:30')
    elif query.data == 'europeaneconomicarea2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay EUR: 40')
    elif query.data == 'uganda2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay UGX: 70,000')
    elif query.data == 'westafricancfafrancbceao2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay CFA: 15,000')
    elif query.data == 'canada2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay CAD: 40')
    elif query.data == 'Unitedkingdom2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https/ to pay GBP: 20')
    elif query.data == 'southafrica2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay R: 500')
    elif query.data == 'ghana2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay GHC: 400')
    elif query.data == 'morocco2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay MAD: 300')
    elif query.data == 'zambia2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay ZMW: 600')
    elif query.data == 'malawi2':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay MWK: 50,000')
    elif query.data == 'tanzania3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay TZS: 80,000')
    elif query.data == 'nigeria3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay NGN: 50,000')
    elif query.data == 'paywithcryptocurrency3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='binance.jpg',
            caption="<b>Copy your preferred address to make a monthly subscription of $50 for HT/FT \n- Binance ID: 797057741\n- TRC20 Address: TDwiXoR9N1U1WVmLKyC9NPAG6ceYfzJjXc\n-Bit coin Address: 1AGcSgoYB429QHDCT1Z5EkgJoE54QgmWJk\n\nThen send payment screenshot here: contact 👉 @mastermindx0</b>",parse_mode='HTML')
    elif query.data == 'kenya3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay KSH: 4,500')
    elif query.data == 'rwanda3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay RWF: 70,000')
    elif query.data == 'unitedstates3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay USD: 50')
    elif query.data == 'europeaneconomicarea3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay EUR: 50')
    elif query.data == 'uganda3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay UGX: 70,000')
    elif query.data == 'westafricancfafrancbceao3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay CFA: 20,000')
    elif query.data == 'canada3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay CAD: 60')
    elif query.data == 'unitedkingdom3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay GBP: 35')
    elif query.data == 'southafrica3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay R: 600')
    elif query.data == 'ghana3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay GHS: 600')
    elif query.data == 'morocco3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay MAD: 500')
    elif query.data == 'zambia3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0 to pay ZMW: 800')
    elif query.data == 'malawi3':
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo='payment.jpg',
            caption='if asked to pay with credit card,click the button shown on this image, to choose a local mobile or bank payment method.\n\nplease click these link: https://t.me/mastermindx0  to pay MWK: 70,000')


async def tips_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "  🔥🔥🔥🔥🔥TODAY'S TIP!🔥🔥🔥🔥\n ------------------------------------------------\n              📅 06 JUL 2025\n\n              🔸 League👉 FINLAND\n\n               ⚽️ Mikkeli vs EPS\n\n                ➡️  Pick: Over2.5(1.62)\n\n              🕙 Time: 18:30\n\nFor more accurate predicts subscribe here 👑(/vip)")


async def freetiphistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "  🎖🎖🎖FREE TIP HISTORY🎖🎖🎖\n ------------------------------------------------\n              📅  05 JUL 2025\n\n              🔸 League👉 NORWAY\n\n               ⚽️  Tromso vs Molde\n\n               ➡️  Pick: Over2.5(1.90)\n\n              🪐 Results  1:0 \n\n  \n\n\n               📅 04 JUl 2025\n\n              🔸 League👉 FIFA\n\n               ⚽️ Fluminense vs Al Hilal\n\n                ➡️  Pick: GG/BTTS(2.10)\n\n              🪐 Results  2:1✅\n\n 🏅🏅 WON SUCCESSFULLY!!!🏅🏅\n\nFor more accurate predicts subscribe here 👑(/vip)")

async def sub_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

async def end_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.delete("thank you")


async def viphistory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "  🏆🏆🏆🏆VIP HISTORY🏆🏆🏆🏆\n ------------------------------------------------\n              📅 05 JUL 2025\n\n    👇👇VIP 2-4 ODDS RESULTS👇👇\n\n              🔸 League👉 IRELAND\n\n               ⚽️  Sligo vs Shamrock\n\n               ➡️  Pick: GG/BTTS(2.10)\n\n              🪐 Results  2:2 ✅\n\n🔸 League👉 NORWAY\n\n               ⚽️  Viking vs stromsgodset\n\n               ➡️  Pick: 1 (1.44)\n\n              🪐 Results   1:0 ✅\n  🏅🏅 WON SUCCESSFULLY!!!🏅🏅\n\nFor more accurate predicts subscribe here 👑(/vip)\n-----------------------------\n  👇👇VIP 10+ ODDS👇👇\n\n🔸 League👉 NORWAY\n\n               ⚽️  Valerenga vs Fredrikstad\n\n               ➡️  Pick: x(3.40)\n\n             🪐 Results  1:1 ✅\n\n🔸 League👉 ROMANIA\n\n               ⚽️  FCSB vs CFR\n\n               ➡️  Pick: 1&GG(4.40)\n\n              🪐 Results  2:1 ✅\n\n 🏅🏅 WON SUCCESSFULLY!!!🏅🏅\nFor more accurate predicts subscribe here 👑(/vip)\n--------------------------------\n     👇👇HT-FT RESULTS!!👇👇\n\n🔸 League👉 FINLAND\n\n               ⚽️  SJK vs Ilves\n\n               ➡️  Pick: HT-FT👉2X (15.00)\n\n              🪐 Results  HT 0:1 FT 1:1 ✅\n  🏅🏅 WON SUCCESSFULLY!!!🏅🏅\n\nFor more accurate predicts subscribe here 👑(/vip)")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please Contact us through link: @mastermindx0 ")

SUBSCRIBERS_FILE='subscribers.json'

try:
    with open(SUBSCRIBERS_FILE, 'r') as f:
        subscribers = json.load(f)
except FileNotFoundError:
    subscribers = {}

def save_subscribers(subscribers):
    with open(SUBSCRIBERS_FILE, 'w') as f:
        json.dump(subscribers, f)

async def handle_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    plan=update.message.text.upper()
    if plan in ['3-10vipodds','10+vipodds','ht/ft']:
        user_id= str(update.message.from_user.id)
        subscribers[user_id]=plan
        save_subscribers(subscribers)
        await update.message.reply_text(f'you are subscribed to {plan}')
    else:
        await update.message.reply_text('sorry you are not subscribed use /vip to subscribe')

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE, plan=None):
    user_id=str(update.message.from_user.id)
    if user_id in subscribers:
        del subscribers[user_id]
        save_subscribers(subscribers)
        await update.message.reply_text(f'you are subscribed to {plan}')
    else:
        await update.message.reply_text('you are not subscribed use /vip to subscribe')


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE, plan=None):
    user_id=str(update.message.from_user.id)
    if user_id in subscribers:
        del subscribers[user_id]
        save_subscribers(subscribers)
        await update.message.reply_text(f'you have been unsubscribed from {plan}')
    else:
        await update.message.reply_text('you are not subscribed use /vip to subscribe')

async def send_daily_tips(app):
    for user_id, plan in subscribers.items():
        tips= f'here are your daily tips for plan: {plan}'
        try:
            await app.bot.send_message(chat_id=int(user_id), text=tips)
        except:
            print(f'failed to send to {user_id}:{e}')




def daily_message(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.context
    context.bot.send_message(chat_id=chat_id, text="🌞 Good morning! check for your today's tip. /start")
    context.job_queue.run_daily(callback=daily_message, time=time(hour=9, minute=0), days=(0, 1, 2, 3, 4, 5, 6), context=chat_id,
        name=f"daily_message_{chat_id}")

    import threading

    WEBHOOK_URL = "https://mastermind-j7f9.onrender.com/webhook"

    def set_webhook_async():
        import time
        time.sleep(3)  # wait for server to start
        success = application.bot.set_webhook(WEBHOOK_URL)
        print("Webhook set successfully ✅" if success else "Failed to set webhook ❌")

    # Start webhook setup in background
    threading.Thread(target=set_webhook_async).start()




if __name__ == '__main__':
    print('starting the bot...')
    app = Application.builder().token(TOKEN).build()

    # commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('vip', vip_command))
    app.add_handler(CommandHandler('tips', tips_command))
    app.add_handler(CommandHandler('viphistory', viphistory_command))
    app.add_handler(CommandHandler('freetiphistory', freetiphistory_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(CallbackQueryHandler(sub_button_handler))
    app.add_handler(CommandHandler('end', end_command))
    app.add_handler(CommandHandler('broadcast', broadcast))


    print("bot is running...")
    app.run_polling(poll_interval=1)

