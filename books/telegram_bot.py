"""
Telegram Bot — Webhook based (production uchun)
"""
import os
import json
import logging
import asyncio
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
MINI_APP_URL = os.environ.get('TELEGRAM_MINI_APP_URL', 'https://kitob-javon.vercel.app')

# Bot application singleton
_application = None


def get_application():
    global _application
    if _application is None and BOT_TOKEN:
        from telegram.ext import Application, CommandHandler

        async def start(update: Update, context):
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

        async def help_command(update: Update, context):
            text = (
                "BookZone Yordam\n\n"
                "Buyruqlar:\n"
                "/start - Boshlash\n"
                "/help - Yordam"
            )
            await update.message.reply_text(text)

        _application = Application.builder().token(BOT_TOKEN).build()
        _application.add_handler(CommandHandler("start", start))
        _application.add_handler(CommandHandler("help", help_command))

    return _application


@csrf_exempt
@require_POST
def telegram_webhook(request):
    """Telegram webhook endpoint"""
    app = get_application()
    if not app:
        return JsonResponse({'error': 'Bot not configured'}, status=500)

    try:
        data = json.loads(request.body)
        update = Update.de_json(data, app.bot)

        # Async update'ni sync qilib ishga tushirish
        async def process():
            await app.initialize()
            await app.process_update(update)
            await app.shutdown()

        asyncio.run(process())
        return JsonResponse({'ok': True})
    except Exception as e:
        logger.error(f'Webhook xatosi: {e}', exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
def set_webhook(request):
    """Webhook'ni o'rnatish"""
    import urllib.request
    import urllib.parse

    if not BOT_TOKEN:
        return JsonResponse({'error': 'No token'}, status=500)

    webhook_url = "https://bookjavon-backend.onrender.com/api/telegram/webhook/"
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    params = urllib.parse.urlencode({'url': webhook_url})
    req = urllib.request.Request(f"{api_url}?{params}")
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    return JsonResponse(data)
