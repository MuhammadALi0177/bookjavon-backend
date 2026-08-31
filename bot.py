"""
Telegram Bot - BookZone Mini App
"""
import os, logging
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
MINI_APP_URL = os.environ.get('TELEGRAM_MINI_APP_URL', 'https://kitob-javon.vercel.app')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Mini App tugmasi
    buttons = [[KeyboardButton(text="BookZone ochish", web_app=WebAppInfo(url=MINI_APP_URL))]]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    text = (
        f"Assalomu alaykum, {user.first_name}!\n\n"
        f"BookZone ga xush kelibsiz!\n\n"
        f"O'zbekistondagi kitob almashish platformasi.\n\n"
        f"Kitoblaringizni soting, ijaraga bering yoki almashtiring!\n\n"
        f"Quyidagi tugmani bosib ilovani oching:"
    )

    await update.message.reply_text(text, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "BookZone Yordam\n\n"
        "Buyruqlar:\n"
        "/start - Boshlash\n"
        "/help - Yordam\n\n"
        "Foydalanish:\n"
        "1. \"BookZone ochish\" tugmasini bosing\n"
        "2. Kitob qo'shing yoki katalogdan toping\n"
        "3. Sotish, ijaraga berish yoki barter qiling!"
    )
    await update.message.reply_text(text)


def main():
    if not BOT_TOKEN:
        print("XATO: TELEGRAM_BOT_TOKEN .env faylida topilmadi!")
        return

    print(f"Bot token yuklandi: ...{BOT_TOKEN[-8:]}")
    print(f"Mini App URL: {MINI_APP_URL}")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("Bot ishga tushdi! /start buyrug'ini yuboring.")
    # drop_pending_updates=True eski updatelarni tashlab ketadi
    app.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )


if __name__ == '__main__':
    main()
