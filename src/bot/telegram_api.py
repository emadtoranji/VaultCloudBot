import requests
import json
from src.config.config import TELEGRAM_TOKEN, DEVELOPER_CHAT_ID


class TelegramAPI:

    def send_request_to_api(self, method, data, timeout=5):
        response = requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}',
            data=data,
            timeout=timeout
        )
        try:
            result = response.json()
            if not response.ok:
                self.bug_report(json.dumps(result))
        except ValueError:
            result = {"ok": False, "error": "Invalid JSON response"}
        return result

    def send_message(self, chat_id, text, reply_markup=None):
        res = self.send_request_to_api('sendMessage', {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': reply_markup
        })
        return res

    def bug_report(self, text):
        self.send_message(chat_id=DEVELOPER_CHAT_ID, text=f"DEVELOPER BUG REPORT\n\nMessage: {text}")
        # raise Exception(text)
