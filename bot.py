import telebot
import random
import time
from datetime import datetime, timedelta

BOT_TOKEN = '7707538907:AAGuf4WXxDOHfe9FV00ReTv817xU08smaaw'
bot = telebot.TeleBot(BOT_TOKEN)

ADMIN_ID = 6430066760
CHANNELS = ['@MKClubOfficial', '@FreeSourceCodeHub', '@ez_75uB_qYoyYjQ1']

accounts = [
    "leranthonychang@icloud.com : E01$t10#$1997 | United States",
    "iven.estudiante@gmail.com : 0408Dayana | United States",
    # (add the rest here)
]

last_generated = {}
secret_codes = {}
used_codes = {}

def is_joined(user_id):
    for ch in CHANNELS:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status not in ['member', 'administrator', 'creator']:
                return False
        except:
            return False
    return True

@bot.message_handler(commands=['start'])
def start(message):
    if not is_joined(message.from_user.id):
        join_text = "🛑 Please join all channels first:\n"
        for ch in CHANNELS:
            join_text += f"➡️ {ch}\n"
        join_text += "\nThen press /start again."
        bot.send_message(message.chat.id, join_text)
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton("🎁 Generate", callback_data="generate"))
        bot.send_message(message.chat.id, "🎉 Welcome! Click below to get your Crunchyroll account.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "generate")
def generate_account(call):
    user_id = call.from_user.id
    if not is_joined(user_id):
        bot.answer_callback_query(call.id, "❗ Please join all channels first.")
        return

    now = datetime.now()
    if user_id in last_generated and now < last_generated[user_id]:
        remaining = last_generated[user_id] - now
        bot.send_message(call.message.chat.id, f"⏳ Please wait {remaining.seconds//3600}h {(remaining.seconds//60)%60}m before generating again.")
        return

    if not accounts:
        bot.send_message(call.message.chat.id, "⏳ How long will it take time.")
        return

    account = accounts.pop(0)
    last_generated[user_id] = now + timedelta(hours=24)
    bot.send_message(call.message.chat.id, f"🎉 Your Crunchyroll Account:\n\n`{account}`", parse_mode="Markdown")

@bot.message_handler(commands=['gensecretcode'])
def gen_secret_code(message):
    if message.from_user.id != ADMIN_ID:
        return
    code = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=8))
    secret_codes[code] = time.time()
    bot.send_message(message.chat.id, f"🔐 Secret Code: `{code}`", parse_mode="Markdown")

@bot.message_handler(commands=['Secretcode'])
def ask_code(message):
    if not is_joined(message.from_user.id):
        bot.send_message(message.chat.id, "🛑 Please join all channels before using this feature.")
        return
    sent = bot.send_message(message.chat.id, "✏️ Send your secret code:")
    bot.register_next_step_handler(sent, process_code)

def process_code(message):
    user_id = message.from_user.id
    code = message.text.strip().upper()

    if code in used_codes:
        bot.send_message(message.chat.id, "❌ This code has already been used.")
        return

    if code not in secret_codes:
        bot.send_message(message.chat.id, "❌ Invalid code.")
        return

    now = time.time()
    if now - secret_codes[code] < 3600:
        if not accounts:
            bot.send_message(message.chat.id, "⏳ How long will it take time.")
            return
        account = accounts.pop(0)
        used_codes[code] = True
        bot.send_message(message.chat.id, f"✅ Here's your Crunchyroll account:\n\n`{account}`", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "⏳ This code has expired.")

bot.polling()
