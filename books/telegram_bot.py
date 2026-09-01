"""
Telegram Bot — Webhook (eng oddiy variant)
Faqat HTTP requests ishlatadi, telegram library kerak emas
"""
import os
import json
import logging
import urllib.request
import urllib.parse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)

MINI_APP_URL = 'https://bookjavon-app.onrender.com'


def get_bot_token():
    """Token har safar so'rov vaqtida o'qiladi — module import emas"""
    return os.environ.get('TELEGRAM_BOT_TOKEN', '')


def send_message(chat_id, text, reply_markup=None):
    """Telegram API orqali xabar yuborish"""
    token = get_bot_token()
    if not token:
        logger.error('TELEGRAM_BOT_TOKEN topilmadi!')
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    data = urllib.parse.urlencode(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data)
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        logger.error(f'Telegram xabar yuborishda xato: {e}')


def handle_message(message):
    """Xabarni qayta ishlash"""
    text = message.get('text', '')
    # Telegram "from" jo'natadi, "from_user" emas!
    user = message.get('from', {})
    chat = message.get('chat', {})
    chat_id = chat.get('id')
    first_name = user.get('first_name', 'Foydalanuvchi')

    if not chat_id:
        return

    if text == '/start':
        reply_markup = {
            "inline_keyboard": [[
                {"text": "📚 BookZone ochish", "web_app": {"url": MINI_APP_URL}}
            ]]
        }
        response = (
            f"Assalomu alaykum, {first_name}! 👋\n\n"
            f"📚 BookZone ga xush kelibsiz!\n\n"
            f"O'zbekistondagi kitob almashish platformasi.\n\n"
            f"Kitoblaringizni soting, ijaraga bering yoki almashtiring!\n\n"
            f"Quyidagi tugmani bosib ilovani oching:"
        )
        send_message(chat_id, response, reply_markup)

    elif text == '/help':
        response = (
            "📚 BookZone Yordam\n\n"
            "Buyruqlar:\n"
            "/start - Boshlash\n"
            "/help - Yordam"
        )
        send_message(chat_id, response)

    else:
        response = "📚 Buyruqlar: /start yoki /help"
        send_message(chat_id, response)


@csrf_exempt
@require_POST
def telegram_webhook(request):
    """Telegram webhook endpoint"""
    try:
        data = json.loads(request.body)

        if 'message' in data:
            handle_message(data['message'])

        return JsonResponse({'ok': True})
    except Exception as e:
        logger.error(f'Webhook xatosi: {e}', exc_info=True)
        return JsonResponse({'ok': True})  # Telegram ga doimo 200 qaytarish


@csrf_exempt
def set_webhook(request):
    """Webhook'ni o'rnatish"""
    token = get_bot_token()
    if not token:
        return JsonResponse({'error': 'No token'}, status=500)

    webhook_url = f'{MINI_APP_URL}/api/telegram/webhook/'
    api_url = f"https://api.telegram.org/bot{token}/setWebhook"
    params = urllib.parse.urlencode({'url': webhook_url})
    req = urllib.request.Request(f"{api_url}?{params}")
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    return JsonResponse(data)
