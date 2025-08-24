import json


class ReplyMarkup:
    """
    Create Telegram Bot Keyboards
    """

    def __init__(self, language):
        self.language = language

    @staticmethod
    def create_keyboard(data):
        if data:
            return json.dumps({'keyboard': data, 'resize_keyboard': True})
        else:
            return None

    @staticmethod
    def create_inline_keyboard(data):
        if data:
            return {'inline_keyboard': data}
        else:
            return None

    def start(self):
        return self.create_keyboard([[self.language.get('admin_menu_button', 'Admin Menu')]])

    def admin(self):
        return self.create_keyboard([[self.language.get('start_menu_button', 'Start Menu')]])
