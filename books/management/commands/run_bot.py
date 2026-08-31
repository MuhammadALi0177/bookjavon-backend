"""
Management command: python manage.py run_bot
Render'da Telegram bot'ni ishga tushiradi
"""
import os
import logging
from django.core.management.base import BaseCommand
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mini_app_url = os.environ.get('TELEGRAM_MINI_APP_URL', 'https://kitob-javon.vercel.app')

    buttons = [[KeyboardButton(text="BookZone ochish", web_app=WebAppInfo(url=mini_app_url))]]
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


class Command(BaseCommand):
    help = 'Telegram bot ishga tushiradi'

    def handle(self, *args, **options):
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        if not bot_token:
            self.stderr.write(self.style.ERROR('TELEGRAM_BOT_TOKEN topilmadi!'))
            return

        self.stdout.write(self.style.SUCCESS(f'Bot token yuklandi: ...{bot_token[-8:]}'))
        self.stdout.write(self.style.SUCCESS('Bot ishga tushdi!'))

        app = Application.builder().token(bot_token).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))

        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
