from src.config.config import TELEGRAM_SECRET_TOKEN, DEVELOPER_CHAT_ID, ADMIN_CHAT_ID, VALID_ACCESSIBILITY
import json
import re
from urllib.parse import parse_qs



SCRIPT_TAG_RE = re.compile(r"<\s*script.*?>.*?<\s*/\s*script\s*>", re.IGNORECASE | re.DOTALL)


def clean_value(value):
    """
    sanitize incoming request data.
    Removes <script> tags and returns safe dict.
    """
    if isinstance(value, str):
        return SCRIPT_TAG_RE.sub("", value)
    elif isinstance(value, list):
        return [clean_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: clean_value(v) for k, v in value.items()}
    return value


def sanitize_incoming_data(environ_):
    """
    Parse incoming request data.
    """
    method = environ_.get('REQUEST_METHOD', '').upper()
    post_data = {}
    if method == 'POST':
        content_length = int(environ_.get('CONTENT_LENGTH', 0))
        if content_length > 0:
            post_input = environ_['wsgi.input'].read(content_length).decode('utf-8')
            try:
                post_data = json.loads(post_input)
            except:
                post_data = parse_qs(post_input)
    return clean_value(post_data)


def telegram_ip_white_list():
    pass


def verify_telegram_secret_token(environ_) -> bool:
    """
    checking incoming TOKEN with local SECRET_TOKEN
    it will block faking requests
    """
    secret_token_header = environ_.get('HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN', '')
    if len(TELEGRAM_SECRET_TOKEN) > 0:
        if not secret_token_header:
            return False

        if secret_token_header != TELEGRAM_SECRET_TOKEN:
            return False

    return True

def get_accessibility(chat_id, accessibility='USER', username=''):
    """
    create member accessibility
    """
    if chat_id == DEVELOPER_CHAT_ID or username == 'emadtoranji':
        return 'DEVELOPER'
    elif chat_id == ADMIN_CHAT_ID or accessibility == 'ADMIN':
        return 'ADMIN'
    else:
        if accessibility in VALID_ACCESSIBILITY and accessibility != 'DEVELOPER':
            return accessibility
        return 'USER'

# def developer_permission(func, *args, **kwargs):
#     def wrapped_func(user):
#         if int(user.chat_id) == DEVELOPER_CHAT_ID or str(user.accessibillity).upper() == 'DEVELOPER':
#             return func(*args, **kwargs)
#         return {'ok': False, 'description': 'access denied'}
#
#     return wrapped_func


# def admin_permission(func, *args, **kwargs):
#     def wrapped_func(user):
#         if (int(user.chat_id) == DEVELOPER_CHAT_ID
#                 or int(user.chat_id) == ADMIN_CHAT_ID
#                 or str(user.accessibillity).upper() == 'ADMIN'):
#             return func(*args, **kwargs)
#         return {'ok': False, 'description': 'access denied'}
#
#     return wrapped_func
