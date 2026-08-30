"""
Token-based authentication for BookZone API.
Simple token auth for demo mode + Telegram WebApp auth.
"""
import hashlib
import hmac
import time
from urllib.parse import unquote

from django.conf import settings
from rest_framework import authentication, exceptions


class TelegramWebAppAuth(authentication.BaseAuthentication):
    """
    Authenticate via Telegram WebApp initData.
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('tma '):
            return None

        token = auth_header[4:]
        return self._verify_init_data(token)

    def _verify_init_data(self, init_data_str):
        from books.models import User
        try:
            pairs = {}
            hash_value = None
            for item in init_data_str.split('&'):
                key, value = item.split('=', 1)
                key = unquote(key)
                value = unquote(value)
                if key == 'hash':
                    hash_value = value
                else:
                    pairs[key] = value

            if not hash_value:
                raise exceptions.AuthenticationFailed('Missing hash')

            auth_date = int(pairs.get('auth_date', 0))
            if time.time() - auth_date > 86400:
                raise exceptions.AuthenticationFailed('Init data expired')

            data_check_arr = []
            for key in sorted(pairs.keys()):
                if key != 'hash':
                    data_check_arr.append(f'{key}={pairs[key]}')
            data_check_string = '\n'.join(data_check_arr)

            bot_token = settings.TELEGRAM_BOT_TOKEN
            secret_key = hmac.new(
                bot_token.encode(), b'WebAppData', hashlib.sha256
            ).digest()
            computed_hash = hmac.new(
                secret_key,
                data_check_string.encode(),
                hashlib.sha256
            ).hexdigest()

            if computed_hash != hash_value:
                raise exceptions.AuthenticationFailed('Invalid hash')

            import json
            user_data = json.loads(pairs.get('user', '{}'))
            telegram_id = user_data.get('id')
            if not telegram_id:
                raise exceptions.AuthenticationFailed('Missing user ID')

            user, created = User.objects.get_or_create(
                telegram_id=telegram_id,
                defaults={
                    'telegram_username': user_data.get('username', ''),
                    'full_name': f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip(),
                }
            )

            return (user, init_data_str)

        except (ValueError, KeyError) as e:
            raise exceptions.AuthenticationFailed(f'Invalid init data: {str(e)}')


class DemoTokenAuth(authentication.BaseAuthentication):
    """
    Simple token auth for demo mode.
    Header: Authorization: demo <token>
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('demo '):
            return None

        token_key = auth_header[5:]
        try:
            from books.models import SimpleToken
            token = SimpleToken.objects.select_related('user').get(key=token_key)
            return (token.user, token_key)
        except SimpleToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid demo token')
