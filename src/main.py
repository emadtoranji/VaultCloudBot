import traceback
from src.bot.telegram import TelegramBase
from src.bot.telegram_api import TelegramAPI
from src.database.models import init_database
from src.utils.validation import sanitize_incoming_data


def run_script(sanitized, environ):
    init_database()
    TelegramBase.create(sanitized, environ)


def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    sanitized = sanitize_incoming_data(environ)
    try:
        run_script(sanitized, environ)
        return [b"Script executed successfully"]
    except Exception as e:
        msg = f"Error occurred: {str(e)}"
        details = traceback.format_exc()
        TelegramAPI().bug_report(f"\n{msg}\n\n{details}")
        return [msg.encode()]
