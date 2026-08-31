import os
import logging
import threading
from django.apps import AppConfig

logger = logging.getLogger(__name__)


def start_telegram_bot():
    """Background thread'da Telegram bot'ni ishga tushiradi"""
    try:
        from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
        from telegram.ext import Application, CommandHandler, ContextTypes

        BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
        MINI_APP_URL = os.environ.get('TELEGRAM_MINI_APP_URL', 'https://kitob-javon.vercel.app')

        if not BOT_TOKEN:
            logger.warning('TELEGRAM_BOT_TOKEN topilmadi — bot ishlamaydi')
            return

        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user
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
                "/help - Yordam"
            )
            await update.message.reply_text(text)

        logger.info(f'Telegram bot ishga tushmoqda... Mini App: {MINI_APP_URL}')
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    except Exception as e:
        logger.error(f'Telegram bot xatosi: {e}')


class BooksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'books'
    verbose_name = 'Kitoblar'

    def ready(self):
        """Django ishga tushganda bot'ni background thread'da boshlash"""
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        # Dev mode'da faqat reloader process'da ishga tushirish
        if debug and os.environ.get('RUN_MAIN') != 'true':
            return
        thread = threading.Thread(target=start_telegram_bot, daemon=True)
        thread.start()
        logger.info('Telegram bot background thread ishga tushdi')
