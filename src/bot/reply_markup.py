import json


class ReplyMarkup:
    """
    Create Telegram Bot Keyboards
    """

    def __init__(self, language, accessibility='USER'):
        self.language = language
        self.__accessibility = accessibility

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
        __keyboard = []
        if self.__accessibility in ('ADMIN', 'DEVELOPER'):
            __keyboard += [[self.language.get('admin_section', {}).get('admin_menu_button', '/admin')]]
        return self.create_keyboard(__keyboard)

    def return_to_admin(self):
        return self.create_keyboard(
            [[self.language.get('admin_section', {}).get('return_to_admin_menu_message', '/admin')]]
        )

    def add_a_new_file_finish_button(self):
        return self.create_keyboard(
            [
                [
                    self.language.get('admin_section', {}).get(
                        'add_a_new_file_finish_button', '/admin_add_a_new_file_finish'
                    )
                ],
                [self.language.get('admin_section', {}).get('return_to_admin_menu_message', '/admin')]
            ],
        )

    def admin(self):
        return self.create_keyboard(
            [
                [self.language.get('admin_section', {}).get('add_a_new_file', '/admin_add_new_file')],
                [self.language.get('global_section', {}).get('return_to_start_menu_button', '/start')]
            ]
        )
