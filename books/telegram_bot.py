"""
Telegram Bot — Webhook based (production uchun)
"""
import os
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
MINI_APP_URL = os.environ.get('TELEGRAM_MINI_APP_URL', 'https://kitob-javon.vercel.app')


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


# Application singleton
_app = None


def get_application():
    global _app
    if _app is None and BOT_TOKEN:
        _app = Application.builder().token(BOT_TOKEN).build()
        _app.add_handler(CommandHandler("start", start))
        _app.add_handler(CommandHandler("help", help_command))
    return _app


@csrf_exempt
@require_POST
def telegram_webhook(request):
    """Telegram webhook endpoint"""
    app = get_application()
    if not app:
        return JsonResponse({'error': 'Bot not configured'}, status=500)

    try:
        import json
        data = json.loads(request.body)
        update = Update.de_json(data, app.bot)
        import asyncio
        loop = asyncio.new_event_loop()
        loop.run_until_complete(app.process_update(update))
        loop.close()
        return JsonResponse({'ok': True})
    except Exception as e:
        logger.error(f'Webhook xatosi: {e}')
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def set_webhook(request):
    """Webhook'ni o'rnatish — faqat GET"""
    import requests
    if not BOT_TOKEN:
        return JsonResponse({'error': 'No token'}, status=500)

    webhook_url = f"https://bookjavon-backend.onrender.com/api/telegram/webhook/"
    resp = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
        params={"url": webhook_url}
    )
    return JsonResponse(resp.json())
