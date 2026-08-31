"""
Telegram Bot — Webhook based (production uchun)
Oddiy Bot API ishlatadi, Application framework emas
"""
import os
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from telegram import Bot, Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
MINI_APP_URL = os.environ.get('TELEGRAM_MINI_APP_URL', 'https://kitob-javon.vercel.app')


async def handle_message(message):
    """Xabarni qayta ishlash"""
    bot = Bot(token=BOT_TOKEN)
    text = message.text or ''
    user = message.from_user
    chat_id = message.chat.id

    if text == '/start':
        buttons = [[KeyboardButton(text="BookZone ochish", web_app=WebAppInfo(url=MINI_APP_URL))]]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        response = (
            f"Assalomu alaykum, {user.first_name}!\n\n"
            f"BookZone ga xush kelibsiz!\n\n"
            f"O'zbekistondagi kitob almashish platformasi.\n\n"
            f"Kitoblaringizni soting, ijaraga bering yoki almashtiring!\n\n"
            f"Quyidagi tugmani bosib ilovani oching:"
        )
        await bot.send_message(chat_id=chat_id, text=response, reply_markup=reply_markup)

    elif text == '/help':
        response = (
            "BookZone Yordam\n\n"
            "Buyruqlar:\n"
            "/start - Boshlash\n"
            "/help - Yordam"
        )
        await bot.send_message(chat_id=chat_id, text=response)

    else:
        response = (
            "Buyruqlar:\n"
            "/start - Boshlash\n"
            "/help - Yordam"
        )
        await bot.send_message(chat_id=chat_id, text=response)


@csrf_exempt
@require_POST
def telegram_webhook(request):
    """Telegram webhook endpoint"""
    if not BOT_TOKEN:
        return JsonResponse({'error': 'Bot not configured'}, status=500)

    try:
        data = json.loads(request.body)

        # Update ni parse qilish
        if 'message' in data:
            import asyncio
            asyncio.run(handle_message(data['message']))

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
