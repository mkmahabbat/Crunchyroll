import logging
import random
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# --- Configuration ---
TOKEN = "7707538907:AAGuf4WXxDOHfe9FV00ReTv817xU08smaaw"
ADMIN_ID = 6430066760
REQUIRED_CHANNELS = [
    "https://t.me/MKClubOfficial",
    "https://t.me/+ez_75uB_qYoyYjQ1",
    "https://t.me/FreeSourceCodeHub"
]

# --- Data Storage ---
last_generated = {}
secret_codes = {}

# --- Logging ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# --- Start Command ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    buttons = [[InlineKeyboardButton("📢 Join Channel", url=url)] for url in REQUIRED_CHANNELS]
    buttons.append([InlineKeyboardButton("🎁 Generate Account", callback_data="generate")])
    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        f"👋 Hello, {user.first_name}!\n\n"
        "✅ Please join all the channels below to continue.\n"
        "🎉 Once done, tap the button below to get your Crunchyroll account.",
        reply_markup=keyboard
    )

# --- Generate Button ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "generate":
        now = time.time()
        if user_id in last_generated and now - last_generated[user_id] < 86400:
            await query.message.reply_text("⏳ You can only generate one account every 24 hours. Please try again later.")
            return
        try:
            with open("accounts.txt", "r") as f:
                accounts = [line.strip() for line in f if line.strip()]
            if not accounts:
                await query.message.reply_text("❌ No accounts available.")
                return
            account = accounts.pop(0)
            with open("accounts.txt", "w") as f:
                f.write("\\n".join(accounts))
            last_generated[user_id] = now
            await query.message.reply_text(f"🎊 Your Crunchyroll account:\n\n`{account}`", parse_mode="Markdown")
        except FileNotFoundError:
            await query.message.reply_text("❌ accounts.txt not found.")

# --- Admin Secret Code Generator ---
async def gensecretcode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    code = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))
    secret_codes[code] = {"used": False, "timestamp": 0, "user": None}
    await update.message.reply_text(f"🔐 Generated Secret Code:\n\n`{code}`", parse_mode="Markdown")

# --- User Secret Code Command ---
async def secretcode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔐 Please send your secret code now.")

# --- Handle Text Messages (Codes) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    code = update.message.text.strip().upper()
    now = time.time()

    if code in secret_codes:
        entry = secret_codes[code]
        if entry["used"]:
            await update.message.reply_text("❌ This secret code has already been used.")
            return
        if entry["user"] and now - entry["timestamp"] < 3600:
            await update.message.reply_text("⏳ Please wait 1 hour before using another code.")
            return
        try:
            with open("accounts.txt", "r") as f:
                accounts = [line.strip() for line in f if line.strip()]
            if not accounts:
                await update.message.reply_text("❌ No accounts available.")
                return
            account = accounts.pop(0)
            with open("accounts.txt", "w") as f:
                f.write("\\n".join(accounts))
            entry["used"] = True
            entry["timestamp"] = now
            entry["user"] = user_id
            await update.message.reply_text(f"🎉 Your Crunchyroll account:\n\n`{account}`", parse_mode="Markdown")
        except FileNotFoundError:
            await update.message.reply_text("❌ accounts.txt not found.")
    else:
        await update.message.reply_text("❌ Invalid secret code.")

# --- Main Entry ---
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gensecretcode", gensecretcode))
    app.add_handler(CommandHandler("Secretcode", secretcode_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
